import mysql.connector
from mysql.connector import errorcode
import pandas as pd

# ——— 请在这里填入您的数据库连接信息 ———
DB_CONFIG = {
    'user': 'root',      # 您的用户名
    'password': '3114423240',  # 您的密码
    'host': 'localhost',          # 您的数据库主机，本地通常是 127.0.0.1
    'database': 'excel_import_db',  # 您要连接的数据库名
    'port': 3306                  # 数据库端口，MySQL 默认为 3306
}

def execute_query(query):
    """
    连接到数据库，执行查询，并返回结果为 Pandas DataFrame。
    """
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        print("数据库连接成功！")
        
        # 使用 pandas 直接从 SQL 查询读取数据，更简洁高效
        df = pd.read_sql(query, cnx)
        
        return df

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ 错误：用户名或密码不正确。")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"❌ 错误：数据库 '{DB_CONFIG['database']}' 不存在。")
        else:
            print(f"❌ 发生未知数据库错误: {err}")
        return None
    except Exception as e:
        print(f"❌ 发生了一个非数据库错误: {e}")
        return None
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
            # print("数据库连接已关闭。")

if __name__ == "__main__":
    # ——— 在这里写下您想执行的 SQL 查询 ———
    # 这是一个示例查询，统计不同拜访目的的数量
    sql_query = """
    SELECT 
        `拜访目的`, 
        COUNT(*) AS '拜访次数'
    FROM 
        visit_record 
    GROUP BY 
        `拜访目的`
    ORDER BY 
        `拜访次数` DESC;
    """
    
    print(f"🚀 正在执行查询: {sql_query}")
    query_result_df = execute_query(sql_query)
    
    if query_result_df is not None:
        print("\n✅ 查询结果:")
        # 设置 pandas 显示所有列，避免结果被折叠
        pd.set_option('display.max_columns', None)
        print(query_result_df) 