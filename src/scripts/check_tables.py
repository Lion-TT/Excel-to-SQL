#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表状态
"""

import pymysql
from src.shared.config import DB_CONFIG

def check_tables():
    """检查数据库中的表"""
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # 查询所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # 检查特定表是否存在
        target_table = 'last_7_days_customer_info'
        cursor.execute(f"SHOW TABLES LIKE '{target_table}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"\n表 '{target_table}' 存在")
            # 查看表结构
            cursor.execute(f"DESCRIBE {target_table}")
            columns = cursor.fetchall()
            print(f"表结构:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print(f"\n表 '{target_table}' 不存在")
            
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"检查表时出错: {e}")

if __name__ == "__main__":
    check_tables() 