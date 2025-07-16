# db_importer.py
# 批量导入多表CSV文件到MySQL数据库
import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from src.shared.config import DB_CONFIG, DATA_SOURCES, get_csv_dir_for_table, get_all_table_names, get_update_strategy, TABLE_PRIMARY_KEYS
from src.shared.config import TABLE_COLUMNS
from src.shared.table_schemas import TABLE_SCHEMAS
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
import time # 导入time模块

# 数据库连接字符串
conn_str = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
engine = create_engine(conn_str, echo=False, pool_recycle=120, pool_pre_ping=True)

def get_csv_files(directory):
    """
    获取指定目录下所有CSV文件路径
    """
    if not os.path.isdir(directory):
        print(f"目录不存在: {directory}")
        return []
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith('.csv')]

def import_csv_to_mysql(csv_path, table_name, chunk_size=20000):
    """
    分块导入单个CSV文件到指定表
    """
    print(f"\n开始导入: {os.path.basename(csv_path)} 到表 '{table_name}' ...")
    try:
        # 检查列名是否有重复
        chunk_iter = pd.read_csv(csv_path, encoding='utf-8-sig', chunksize=chunk_size)
        first_chunk = next(chunk_iter)
        
        # 动态获取期望列名
        original_columns = TABLE_COLUMNS.get(table_name)
        current_columns = list(first_chunk.columns)
        if original_columns:
            print(f"期望的列数: {len(original_columns)}")
            print(f"实际的列数: {len(current_columns)}")
            # 如果列数不匹配或列名被重命名，尝试修正
            if len(current_columns) != len(original_columns) or any('_m' in col for col in current_columns):
                print(f"检测到列名问题，尝试修正...")
                print(f"当前列名: {current_columns[:5]}...")  # 只显示前5个
                # 重新读取CSV，使用原始列名
                chunk_iter = pd.read_csv(csv_path, encoding='utf-8-sig', chunksize=chunk_size, names=original_columns, header=0)
                first_chunk = next(chunk_iter)
                print(f"修正后列名: {list(first_chunk.columns)}")
            else:
                # 重新开始读取，进行实际导入
                chunk_iter = pd.read_csv(csv_path, encoding='utf-8-sig', chunksize=chunk_size)
        else:
            # 没有配置期望列名，直接用CSV的表头
            print(f"未配置期望列名，直接使用CSV表头。实际列数: {len(current_columns)}")
            chunk_iter = pd.read_csv(csv_path, encoding='utf-8-sig', chunksize=chunk_size)
        
        print(f"CSV列数: {len(first_chunk.columns)}")
        print(f"第一个数据块行数: {len(first_chunk)}")
        
        # 进行实际导入
        total = 0
        for i, chunk in enumerate(chunk_iter, 1):
            # 直接导入，不做任何日期格式处理
            chunk.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
            total += len(chunk)
            print(f"  已导入 {total} 行...")
        print(f"导入完成: {os.path.basename(csv_path)}，共导入 {total} 行到表 '{table_name}'。")
        
        # 验证导入结果
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()[0]
            print(f"数据库表 '{table_name}' 当前总行数: {count}")
            
    except Exception as e:
        import traceback
        err_str = str(e)
        print(f"导入失败: {csv_path}，原因: {err_str[:500]}{'...（已截断）' if len(err_str)>500 else ''}")
        tb_lines = traceback.format_exc().splitlines()
        print('\n'.join(tb_lines[:10]))
        if len(tb_lines) > 10:
            print("...（traceback已截断）")

def get_db_columns(table_name, engine):
    """获取数据库中表的字段名和类型，返回dict: 字段名->类型字符串"""
    inspector = inspect(engine)
    columns = {}
    for col in inspector.get_columns(table_name):
        col_type = str(col['type'])
        # 只保留类型主干部分，便于比对
        if '(' in col_type:
            col_type = col_type.split('(')[0].upper()
        else:
            col_type = col_type.upper()
        columns[col['name']] = col_type
    return columns

def table_exists(table_name, engine):
    inspector = inspect(engine)
    return inspector.has_table(table_name)

def truncate_table(table_name, engine):
    """
    清空指定的数据库表。
    """
    print(f"执行清空表操作: {table_name}")
    try:
        with engine.connect() as connection:
            with connection.begin(): # 使用事务确保TRUNCATE被正确执行
                connection.execute(text(f"TRUNCATE TABLE `{table_name}`"))
        print(f"成功清空表: {table_name}")
    except Exception as e:
        print(f"清空表 '{table_name}' 失败: {e}")
        # 重新抛出异常，以便上层调用者可以捕获它
        raise

def sync_table_schema(table_name, engine):
    """
    自动同步table_schemas.py和数据库表结构：新建表、加字段、删字段、类型变更、字段重命名
    """
    schema = TABLE_SCHEMAS[table_name]
    code_columns = {col[0]: col[1] for col in schema['columns']}
    code_col_names = set(code_columns.keys())
    primary_key = schema.get('primary_key')
    rename_map = schema.get('rename', {})

    inspector = inspect(engine)
    with engine.connect() as conn:
        # 1. 新建表
        if not inspector.has_table(table_name):
            col_defs = [f"`{col}` {typ}" for col, typ in schema['columns']]
            pk = f", PRIMARY KEY (`{primary_key}`)" if primary_key else ''
            create_sql = f"CREATE TABLE `{table_name}` ({', '.join(col_defs)}{pk}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
            print(f"[自动建表] {table_name}\n{create_sql}")
            conn.execute(text(create_sql))
            conn.commit()  # 确保提交事务
            return
        # 2. 获取数据库字段
        db_columns = get_db_columns(table_name, engine)
        db_col_names = set(db_columns.keys())
        # 3. 字段重命名
        for old, new in rename_map.items():
            if old in db_col_names and new in code_col_names:
                alter_sql = f"ALTER TABLE `{table_name}` CHANGE `{old}` `{new}` {code_columns[new]};"
                print(f"[自动重命名字段] {old} -> {new}: {alter_sql}")
                try:
                    conn.execute(text(alter_sql))
                except ProgrammingError as e:
                    print(f"[重命名失败] {e}")
        # 4. 加字段
        for col in code_col_names - db_col_names:
            alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {code_columns[col]};"
            print(f"[自动加字段] {col}: {alter_sql}")
            try:
                conn.execute(text(alter_sql))
            except ProgrammingError as e:
                print(f"[加字段失败] {e}")
        # 5. 删字段
        for col in db_col_names - code_col_names:
            alter_sql = f"ALTER TABLE `{table_name}` DROP COLUMN `{col}`;"
            print(f"[自动删字段] {col}: {alter_sql}")
            try:
                conn.execute(text(alter_sql))
            except ProgrammingError as e:
                print(f"[删字段失败] {e}")
        # 6. 类型变更
        for col in code_col_names & db_col_names:
            code_type = code_columns[col].split()[0].upper()
            db_type = db_columns[col].upper()
            if code_type != db_type:
                alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{col}` {code_columns[col]};"
                print(f"[自动类型变更] {col}: {alter_sql}")
                try:
                    conn.execute(text(alter_sql))
                except ProgrammingError as e:
                    print(f"[类型变更失败] {e}")

def import_table(table_name):
    """
    导入指定表的所有CSV文件，根据配置的更新策略选择导入方式
    """
    if table_name not in DATA_SOURCES:
        print(f"错误：表 '{table_name}' 未在配置中找到")
        return

    # 自动同步表结构
    sync_table_schema(table_name, engine)

    csv_dir = get_csv_dir_for_table(table_name)
    csv_files = get_csv_files(csv_dir)
    if not csv_files:
        print(f"在目录 {csv_dir} 下未找到CSV文件。")
        return

    # 获取更新策略
    update_strategy = get_update_strategy(table_name)
    print(f"\n开始导入表 '{table_name}' 的CSV文件...")
    print(f"更新策略: {update_strategy}")
    print(f"CSV目录: {csv_dir}")
    print(f"共找到 {len(csv_files)} 个CSV文件\n")

    # 获取主键字段
    primary_key = TABLE_SCHEMAS[table_name]['primary_key']
    
    try:
        # 合并所有CSV文件
        dfs = []
        for csv_file in csv_files:
            print(f"读取文件: {os.path.basename(csv_file)}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            dfs.append(df)
        
        if not dfs:
            print("没有找到有效的CSV数据")
            return
            
        df_all = pd.concat(dfs, ignore_index=True)
        print(f"CSV文件合并后总行数: {len(df_all)}")
        
        # 根据更新策略处理数据
        if update_strategy == 'truncate':
            # 清空重传策略
            print("执行清空重传策略...")
            with engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                print(f"已清空表 '{table_name}'")
            
            df_to_import = df_all
            print(f"将导入所有 {len(df_to_import)} 行数据")
            
        else:
            # 增量更新策略（默认）
            print("执行增量更新策略...")
            
            # 获取数据库中已存在的主键值，用于去重
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT {primary_key} FROM {table_name}"))
                existing_keys = set(row[0] for row in result.fetchall())
            
            print(f"数据库中已存在 {len(existing_keys)} 条记录")
            
            # 过滤掉已存在的主键，只保留新数据
            if len(existing_keys) > 0:
                df_new = df_all[~df_all[primary_key].isin(existing_keys)]
                print(f"过滤已存在数据后，新增行数: {len(df_new)}")
            else:
                df_new = df_all
                print(f"数据库为空，将导入所有 {len(df_new)} 行数据")
            
            if len(df_new) == 0:
                print("没有新数据需要导入")
                return
            
            df_to_import = df_new
        
        # 对数据进行去重（CSV内部可能有重复）
        before_dedup = len(df_to_import)
        df_to_import = df_to_import.drop_duplicates(subset=[primary_key])
        after_dedup = len(df_to_import)
        print(f"去重后剩余: {after_dedup} 行")
        
        # 根据schema获取日期列名
        date_columns_in_schema = [col[0] for col in TABLE_SCHEMAS[table_name]['columns'] if 'DATE' in col[1].upper()]
        
        # 批量分块插入数据
        chunk_size = 20000
        total_imported = 0
        
        for start in range(0, len(df_to_import), chunk_size):
            chunk = df_to_import.iloc[start:start+chunk_size].copy() # 使用 .copy() 避免 SettingWithCopyWarning
            
            try:
                chunk.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
                total_imported += len(chunk)
                print(f"  已导入 {total_imported} 行数据...")
            except SQLAlchemyError as e:
                print(f"分块插入出错，已跳过本块: {str(e)[:300]}...")
        
        # 验证最终结果
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            final_count = result.fetchone()[0]
            print(f"表 '{table_name}' 导入完成！当前总行数: {final_count}")
            
    except Exception as e:
        import traceback
        err_str = str(e)
        print(f"导入失败: {csv_dir}，原因: {err_str[:500]}{'...（已截断）' if len(err_str)>500 else ''}")
        tb_lines = traceback.format_exc().splitlines()
        print('\n'.join(tb_lines[:10]))
        if len(tb_lines) > 10:
            print("...（traceback已截断）")

def import_dataframe_to_mysql(df, table_name, chunk_size=20000):
    """
    直接将DataFrame分块导入指定表
    """
    print(f"\n开始导入DataFrame到表 '{table_name}' ...")
    max_retries = 3 # 最大重试次数
    initial_delay = 1 # 初始等待秒数

    try:
        # 自动同步表结构，确保表存在
        sync_table_schema(table_name, engine)
        
        # 获取更新策略
        update_strategy = get_update_strategy(table_name)
        primary_key = TABLE_PRIMARY_KEYS.get(table_name) # 从 TABLE_PRIMARY_KEYS 获取主键
        
        # 验证主键字段是否存在
        if primary_key and primary_key not in df.columns:
            print(f"警告: 主键字段 '{primary_key}' 不在DataFrame中，可用字段: {list(df.columns)}")
            # 尝试从schema中获取正确的主键名
            schema_primary_key = TABLE_SCHEMAS[table_name].get('primary_key')
            if schema_primary_key and schema_primary_key in df.columns:
                primary_key = schema_primary_key
                print(f"使用schema中的主键字段: '{primary_key}'")
            else:
                print(f"无法找到有效的主键字段，将按追加方式导入")
                primary_key = None
                update_strategy = 'append'
        
        if not primary_key and update_strategy == 'incremental':
            print(f"警告: 表 '{table_name}' 未配置主键，无法执行增量更新策略。将按追加方式导入。")
            update_strategy = 'append' # 降级为追加

        print(f"更新策略: {update_strategy}")
        if primary_key:
            print(f"主键字段: '{primary_key}'")
        
        # 动态获取期望列名并修正DataFrame列
        original_columns = TABLE_COLUMNS.get(table_name)
        current_columns = list(df.columns)
        
        if original_columns:
            print(f"DataFrame列数: {len(current_columns)}, 配置列数: {len(original_columns)}")
            # 如果列名完全不匹配，但数量匹配，则认为是旧版重命名逻辑，强制使用配置的列名
            if len(current_columns) == len(original_columns) and not set(current_columns).intersection(set(original_columns)):
                 print("检测到列名可能不匹配，强制重命名。")
                 df.columns = original_columns
            else: # 否则，只保留在配置中存在的列，保持顺序
                df = df[[col for col in original_columns if col in current_columns]]
        else:
            print(f"未配置期望列名，使用DataFrame的原始列。列数: {len(current_columns)}")

        print(f"原始DataFrame总行数: {len(df)}")
        
        df_to_import = None

        # 根据更新策略处理数据
        if update_strategy == 'incremental':
            # 增量更新策略
            print("执行增量更新策略...")
            
            # 获取数据库中已存在的主键值
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT `{primary_key}` FROM `{table_name}`"))
                    existing_keys = {row[0] for row in result.fetchall()}
                print(f"数据库中已存在 {len(existing_keys)} 条记录的主键")
            except Exception as e:
                print(f"查询已存在主键失败: {e}，将导入所有数据。")
                existing_keys = set()
            
            # 过滤掉已存在的主键，只保留新数据
            if len(existing_keys) > 0:
                df_new = df[~df[primary_key].isin(existing_keys)]
                print(f"过滤已存在数据后，新增行数: {len(df_new)}")
            else:
                df_new = df
                print(f"数据库为空，将导入所有 {len(df_new)} 行数据")

            df_to_import = df_new
        else:
            # 对于 'truncate' 和 'append' 策略，我们直接使用传入的DataFrame
            # 'truncate' 的清空操作已移至 importer 主控逻辑中
            print("执行追加或清空重传（仅追加数据部分）策略...")
            df_to_import = df
        
        # 对数据进行去重（Excel内部可能有重复，或增量更新后需确保导入的数据无重复）
        if primary_key: # 只有有主键的表才进行去重
            before_dedup = len(df_to_import)
            df_to_import = df_to_import.drop_duplicates(subset=[primary_key])
            after_dedup = len(df_to_import)
            if before_dedup != after_dedup:
                print(f"去重后剩余: {after_dedup} 行 (已去除 {before_dedup - after_dedup} 条重复记录)")
            else:
                print(f"数据去重后无变化，总行数: {after_dedup}")
        else:
            print("未配置主键，跳过DataFrame内部去重。")

        if len(df_to_import) == 0:
            print("经过处理后，没有数据需要导入。")
            return

        print(f"最终将导入 {len(df_to_import)} 行数据。")
        
        # 根据schema获取日期列名
        date_columns_in_schema = [col[0] for col in TABLE_SCHEMAS[table_name]['columns'] if 'DATE' in col[1].upper()]
        
        # 预处理日期列：将NaT转换为None，并设置dtype为object
        for col in date_columns_in_schema:
            if col in df_to_import.columns:
                # 将字符串'NULL'转换为None
                df_to_import[col] = df_to_import[col].replace('NULL', None)
                # 确保是datetime类型，否则转换为object
                if pd.api.types.is_datetime64_any_dtype(df_to_import[col]):
                    df_to_import[col] = df_to_import[col].where(pd.notna(df_to_import[col]), None)
                else:
                    # 尝试转换为日期，失败则设为None
                    df_to_import[col] = pd.to_datetime(df_to_import[col], errors='coerce')
                    df_to_import[col] = df_to_import[col].where(pd.notna(df_to_import[col]), None)
                df_to_import[col] = df_to_import[col].astype(object)

        # 批量分块插入数据
        total = 0
        for start in range(0, len(df_to_import), chunk_size):
            chunk = df_to_import.iloc[start:start+chunk_size]
            for attempt in range(max_retries):
                try:
                    chunk.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
                    total += len(chunk)
                    print(f"  已导入 {total} 行...")
                    break # 成功则退出重试
                except SQLAlchemyError as e:
                    err_str = str(e)
                    print(f"[尝试 {attempt+1}/{max_retries}] 分块插入出错，已跳过本块: {err_str[:300]}...")
                    if "Duplicate entry" in err_str and primary_key:
                        print(f"提示: 可能是主键冲突。请检查更新策略或数据。冲突值：{err_str.split('Duplicate entry ')[1].split(' ')[0] if 'Duplicate entry ' in err_str else 'N/A'}")
                    if attempt < max_retries - 1:
                        time.sleep(initial_delay * (2 ** attempt)) # 指数退避
                    else:
                        raise # 达到最大重试次数，抛出异常
        
        print(f"导入完成: DataFrame，共导入 {total} 行到表 '{table_name}'。")
        
        # 验证导入结果
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()[0]
            print(f"数据库表 '{table_name}' 当前总行数: {count}")
            
    except Exception as e:
        import traceback
        err_str = str(e)
        print(f"导入失败: DataFrame，原因: {err_str[:500]}{'...（已截断）' if len(err_str)>500 else ''}")
        tb_lines = traceback.format_exc().splitlines()
        print('\n'.join(tb_lines[:10]))
        if len(tb_lines) > 10:
            print("...（traceback已截断）")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了表名参数，只导入指定表
        table_name = sys.argv[1]
        import_table(table_name)
    else:
        # 否则导入所有表
        batch_import_all() 