#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表创建功能
"""

import pandas as pd
from src.importers.db_importer import sync_table_schema, engine
from src.shared.table_schemas import TABLE_SCHEMAS

def test_table_creation():
    """测试表创建功能"""
    table_name = 'last_7_days_customer_info'
    
    print(f"测试创建表: {table_name}")
    
    try:
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(engine)
        exists_before = inspector.has_table(table_name)
        print(f"创建前表是否存在: {exists_before}")
        
        if not exists_before:
            # 调用同步表结构函数
            print("调用 sync_table_schema...")
            sync_table_schema(table_name, engine)
            
            # 再次检查表是否存在
            exists_after = inspector.has_table(table_name)
            print(f"创建后表是否存在: {exists_after}")
            
            if exists_after:
                print("✅ 表创建成功！")
                
                # 查看表结构
                with engine.connect() as conn:
                    result = conn.execute(f"DESCRIBE {table_name}")
                    columns = result.fetchall()
                    print(f"表结构:")
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
            else:
                print("❌ 表创建失败！")
        else:
            print("表已存在，无需创建")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_table_creation() 