# config.py
# 集中管理所有数据相关路径和数据库配置，支持多表、多路径管理

import os
import pymysql
from src.shared.table_schemas import TABLE_SCHEMAS

# 尝试从 local_config.py 导入个人配置，如果不存在则从示例文件导入
try:
    from src.shared.local_config import DB_CONFIG, DATA_SOURCES
except ImportError:
    print("警告: 未找到 'src/shared/local_config.py'。")
    print("将使用 'local_config.example.py' 中的示例配置。")
    print("请复制 'local_config.example.py' 为 'local_config.py' 并填入您的真实配置。")
    from src.shared.local_config_example import DB_CONFIG, DATA_SOURCES


# 自动生成每个表的字段名和主键信息
TABLE_COLUMNS = {k: [col[0] for col in v['columns']] for k, v in TABLE_SCHEMAS.items()}
TABLE_PRIMARY_KEYS = {k: v['primary_key'] for k, v in TABLE_SCHEMAS.items()}

# 3. 自动生成CSV目录路径（如果csv_dir为None）
def get_csv_dir(table_name, excel_dir):
    """根据表名和Excel目录，自动生成对应的CSV输出目录"""
    if DATA_SOURCES[table_name]['csv_dir'] is not None:
        return DATA_SOURCES[table_name]['csv_dir']
    else:
        parent_dir = os.path.dirname(excel_dir.rstrip('/\\'))
        return os.path.join(parent_dir, f'csv_output_{table_name}')

# 4. 获取所有配置的表名
def get_all_table_names():
    """获取所有配置的表名列表"""
    return list(DATA_SOURCES.keys())

# 5. 获取指定表的Excel目录
def get_excel_dir(table_name):
    """获取指定表的Excel目录"""
    return DATA_SOURCES[table_name]['excel_dir']

# 6. 获取指定表的CSV目录
def get_csv_dir_for_table(table_name):
    """获取指定表的CSV目录"""
    excel_dir = get_excel_dir(table_name)
    return get_csv_dir(table_name, excel_dir)

# 7. 获取指定表的更新策略
def get_update_strategy(table_name):
    """获取指定表的更新策略
    返回值：
        'incremental' - 增量更新
        'truncate' - 清空重传
    """
    return DATA_SOURCES[table_name].get('update_strategy', 'incremental')

# 8. 数据库连接函数
def get_database_connection(db_config: dict = None):
    """
    获取数据库连接
    
    Args:
        db_config: 数据库配置字典，如果为None则使用默认配置
        
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    config = db_config or DB_CONFIG
    return pymysql.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        port=config['port'],
        charset=config['charset'],
        autocommit=True
    )

# 定义批量导入的组
BATCH_GROUPS = {
    'daily_updates': ['visit_record', 'customer_info', 'new_customer_orders'],
    # 您可以在这里添加更多组，例如:
    # 'my_custom_group': ['table_a', 'table_b'],
}

# 迁移或切换环境时，只需修改本文件中的路径和数据库配置即可。
# 添加新表时，只需在 DATA_SOURCES 中添加新的配置项即可。 