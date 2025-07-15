
# 这是一个示例配置文件。
# 请复制此文件为 `local_config.py`，并填入您的真实数据库配置和文件路径。
# `local_config.py` 文件已被 gitignore，不会被上传到版本库中。

# 1. 数据库连接配置 - 请在此处填入您的真实配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'excel_import_db',
    'port': 3306,
    'charset': 'utf8mb4'
}

# 2. 多表数据源配置 - 请在此处填入您的真实文件路径
DATA_SOURCES = {
    'new_customer_orders': {
        'excel_dir': r'path/to/your/excel_files_for_new_orders',
        'csv_dir': None, # 如果为 None，会自动在 excel_dir 的父目录创建 csv_output_{table_name}
        'update_strategy': 'incremental'  # 可选 'incremental' 或 'truncate'
    },
    'visit_record': {
        'excel_dir': r'path/to/your/excel_files_for_visit_records',
        'csv_dir': None,
        'update_strategy': 'incremental' 
    },
    'customer_info': {
        'excel_dir': r'path/to/your/excel_files_for_customer_info',
        'csv_dir': None,
        'update_strategy': 'truncate'  
    },
    # ... 您可以根据需要添加更多数据源
    # 'last_week_customer_orders': {
    #     'excel_dir': r'path/to/your/excel_files_for_last_week_orders',
    #     'csv_dir': None,
    #     'update_strategy': 'incremental'
    # },
} 