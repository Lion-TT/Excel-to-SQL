#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询查看器
用于查看和管理SQL查询文件
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.exporters.sql_manager import list_queries, get_query, format_query


def show_query_details(query_name):
    """显示查询详细信息"""
    print(f"\n📋 查询详情: {query_name}")
    print("=" * 60)
    
    # 获取原始查询
    original_query = get_query(query_name)
    if not original_query:
        print(f"❌ 查询 '{query_name}' 不存在")
        return
    
    print("📝 原始SQL:")
    print("-" * 40)
    print(original_query)
    print("-" * 40)
    
    # 检查是否有参数
    if '{' in original_query and '}' in original_query:
        print("\n🔧 参数说明:")
        print("-" * 40)
        # 提取参数
        import re
        params = re.findall(r'\{(\w+)\}', original_query)
        for param in params:
            print(f"  • {param}: 需要替换的参数")
        
        print("\n💡 使用示例:")
        print("-" * 40)
        example_params = {}
        for param in params:
            if 'date' in param.lower():
                example_params[param] = '2024-01-01'
            elif 'amount' in param.lower():
                example_params[param] = '1000'
            else:
                example_params[param] = '示例值'
        
        try:
            example_query = format_query(query_name, **example_params)
            print("格式化后的SQL:")
            print(example_query)
        except Exception as e:
            print(f"格式化失败: {e}")


def show_all_queries():
    """显示所有查询"""
    print("📋 所有可用的SQL查询")
    print("=" * 60)
    
    queries = list_queries()
    if not queries:
        print("❌ 没有找到可用的SQL查询")
        return
    
    for i, (query_name, description) in enumerate(queries.items(), 1):
        print(f"{i:2d}. {query_name}")
        print(f"    {description}")
        print()


def show_sql_files():
    """显示SQL文件列表"""
    sql_dir = "sql_queries"
    print(f"📁 SQL文件目录: {sql_dir}")
    print("=" * 60)
    
    if not os.path.exists(sql_dir):
        print("❌ SQL目录不存在")
        return
    
    files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
    if not files:
        print("❌ 没有找到SQL文件")
        return
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(sql_dir, filename)
        file_size = os.path.getsize(file_path)
        print(f"{i:2d}. {filename} ({file_size} bytes)")
    
    print(f"\n📊 总计: {len(files)} 个SQL文件")


def show_file_content(filename):
    """显示SQL文件内容"""
    file_path = os.path.join("sql_queries", filename)
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {filename}")
        return
    
    print(f"\n📄 文件内容: {filename}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")


def main():
    """主函数"""
    print("🔍 SQL查询查看器")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有查询")
        print("2. 查看查询详情")
        print("3. 查看SQL文件列表")
        print("4. 查看SQL文件内容")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            show_all_queries()
            
        elif choice == '2':
            queries = list_queries()
            if not queries:
                print("❌ 没有可用的查询")
                continue
            
            print("\n可用的查询:")
            for i, query_name in enumerate(queries.keys(), 1):
                print(f"{i}. {query_name}")
            
            try:
                idx = int(input("\n请输入查询编号: ")) - 1
                query_names = list(queries.keys())
                if 0 <= idx < len(query_names):
                    show_query_details(query_names[idx])
                else:
                    print("❌ 无效的编号")
            except ValueError:
                print("❌ 请输入有效的数字")
                
        elif choice == '3':
            show_sql_files()
            
        elif choice == '4':
            sql_dir = "sql_queries"
            if not os.path.exists(sql_dir):
                print("❌ SQL目录不存在")
                continue
            
            files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
            if not files:
                print("❌ 没有找到SQL文件")
                continue
            
            print("\nSQL文件:")
            for i, filename in enumerate(files, 1):
                print(f"{i}. {filename}")
            
            try:
                idx = int(input("\n请输入文件编号: ")) - 1
                if 0 <= idx < len(files):
                    show_file_content(files[idx])
                else:
                    print("❌ 无效的编号")
            except ValueError:
                print("❌ 请输入有效的数字")
                
        elif choice == '5':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效的选项，请重新选择")


if __name__ == "__main__":
    main() 