import os
import pandas as pd
from src.shared.table_schemas import TABLE_SCHEMAS
from src.shared.config import DATA_SOURCES, get_csv_dir_for_table, get_excel_dir

def convert_excel_to_csv_by_schema(table_name):
    """
    按schema将指定表的所有Excel批量转换为CSV，只保留schema字段，自动补齐缺失列，丢弃多余列。
    """
    columns = [col[0] for col in TABLE_SCHEMAS[table_name]['columns']]
    excel_dir = get_excel_dir(table_name)
    csv_dir = get_csv_dir_for_table(table_name)
    os.makedirs(csv_dir, exist_ok=True)
    files = [f for f in os.listdir(excel_dir) if f.lower().endswith(('.xlsx', '.xls'))]
    print(f"\n[{table_name}] Excel目录: {excel_dir}，共{len(files)}个文件，输出到: {csv_dir}")
    for file in files:
        excel_path = os.path.join(excel_dir, file)
        csv_path = os.path.join(csv_dir, os.path.splitext(file)[0] + '.csv')
        try:
            df = pd.read_excel(excel_path, dtype=str)
            # 只保留schema字段，丢弃多余列
            df = df[[col for col in columns if col in df.columns]]
            # 补齐缺失列
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            df = df[columns]  # 保证列顺序
            # 替换"-"为NULL（不影响日期）
            df = df.replace('-', None)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  已导出: {csv_path}，行数: {len(df)}")
        except Exception as e:
            print(f"  转换失败: {file}，原因: {e}")

def batch_convert_all_tables():
    """
    批量处理所有schema中配置的表
    """
    for table_name in TABLE_SCHEMAS:
        if table_name in DATA_SOURCES:
            convert_excel_to_csv_by_schema(table_name)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        convert_excel_to_csv_by_schema(table_name)
    else:
        batch_convert_all_tables() 