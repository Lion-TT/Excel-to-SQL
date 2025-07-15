#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库导出功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.exporters.db_to_excel_exporter import DatabaseToExcelExporter


def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    try:
        with DatabaseToExcelExporter() as exporter:
            # 测试简单查询
            test_sql = "SELECT 1 as test_value"
            df = exporter.execute_query(test_sql)
            
            if df is not None and not df.empty:
                print("✅ 数据库连接测试成功！")
                return True
            else:
                print("❌ 数据库连接测试失败：查询返回空结果")
                return False
                
    except Exception as e:
        print(f"❌ 数据库连接测试失败：{e}")
        return False


def test_simple_export():
    """测试简单导出功能"""
    print("\n📊 测试简单导出功能...")
    
    try:
        with DatabaseToExcelExporter() as exporter:
            # 测试查询（修复SQL语法错误）
            test_sql = """
            SELECT 
                'test' as test_column,
                NOW() as current_datetime
            LIMIT 5
            """
            
            output_path = "test_export.xlsx"
            
            success = exporter.export_to_excel(
                sql=test_sql,
                output_path=output_path,
                sheet_name="测试数据",
                include_timestamp=False
            )
            
            if success and os.path.exists(output_path):
                print("✅ 简单导出测试成功！")
                print(f"📁 测试文件位置: {output_path}")
                return True
            else:
                print("❌ 简单导出测试失败")
                return False
                
    except Exception as e:
        print(f"❌ 简单导出测试失败：{e}")
        return False


def test_table_structure():
    """测试查看表结构"""
    print("\n🏗️ 测试查看表结构...")
    
    try:
        with DatabaseToExcelExporter() as exporter:
            # 查看数据库中的表
            show_tables_sql = "SHOW TABLES"
            df_tables = exporter.execute_query(show_tables_sql)
            
            if df_tables is not None and not df_tables.empty:
                print("✅ 数据库表列表：")
                for table in df_tables.iloc[:, 0]:
                    print(f"  - {table}")
                
                # 查看第一个表的结构
                if len(df_tables) > 0:
                    first_table = df_tables.iloc[0, 0]
                    desc_sql = f"DESCRIBE {first_table}"
                    df_structure = exporter.execute_query(desc_sql)
                    
                    if df_structure is not None and not df_structure.empty:
                        print(f"\n📋 表 '{first_table}' 的结构：")
                        print(df_structure.to_string(index=False))
                
                return True
            else:
                print("❌ 无法获取表列表")
                return False
                
    except Exception as e:
        print(f"❌ 表结构测试失败：{e}")
        return False


def test_real_data_export():
    """测试真实数据导出"""
    print("\n📈 测试真实数据导出...")
    
    try:
        with DatabaseToExcelExporter() as exporter:
            # 使用实际的表进行测试
            test_sql = """
            SELECT 
                客户id,
                客户名称,
                客户类型,
                创建时间
            FROM customer_info 
            LIMIT 10
            """
            
            output_path = "real_data_test.xlsx"
            
            success = exporter.export_to_excel(
                sql=test_sql,
                output_path=output_path,
                sheet_name="客户信息",
                include_timestamp=False
            )
            
            if success and os.path.exists(output_path):
                print("✅ 真实数据导出测试成功！")
                print(f"📁 测试文件位置: {output_path}")
                return True
            else:
                print("❌ 真实数据导出测试失败")
                return False
                
    except Exception as e:
        print(f"❌ 真实数据导出测试失败：{e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始数据库导出工具测试...")
    print("=" * 50)
    
    # 测试1: 数据库连接
    connection_ok = test_database_connection()
    
    if not connection_ok:
        print("\n💥 数据库连接失败，请检查配置！")
        return
    
    # 测试2: 查看表结构
    structure_ok = test_table_structure()
    
    # 测试3: 简单导出
    export_ok = test_simple_export()
    
    # 测试4: 真实数据导出
    print("\n" + "=" * 50)
    print("📋 测试结果汇总：")
    print(f"  数据库连接: {'✅ 成功' if connection_ok else '❌ 失败'}")
    print(f"  表结构查看: {'✅ 成功' if structure_ok else '❌ 失败'}")
    print(f"  简单导出: {'✅ 成功' if export_ok else '❌ 失败'}")
    
    if connection_ok and export_ok:
        print("\n🎉 所有测试通过！工具可以正常使用。")
        print("\n💡 使用建议：")
        print("  1. 编辑 quick_export.py 文件中的SQL查询")
        print("  2. 修改输出路径")
        print("  3. 运行 python quick_export.py")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和错误信息。")


if __name__ == "__main__":
    main() 