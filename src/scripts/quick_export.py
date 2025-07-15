#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速数据库导出工具
简单易用的数据库到Excel导出脚本
支持从SQL文件加载查询
支持命令行参数调用
"""

import os
import sys
import pandas as pd
import pymysql
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.shared.config import DB_CONFIG
from src.exporters.sql_manager import get_query, format_query, list_queries


def parse_cmd_args():
    """
    支持如下调用方式：
    python quick_export.py 查询名 [参数1=值1 参数2=值2 ...] [--output 输出文件名] [--sheet 工作表名]
    """
    parser = argparse.ArgumentParser(description="数据库导出工具")
    parser.add_argument('query', nargs='?', help='查询名称')
    parser.add_argument('params', nargs='*', help='参数，格式为 key=value')
    parser.add_argument('--output', type=str, help='输出Excel文件路径')
    parser.add_argument('--sheet', type=str, help='Excel工作表名称')
    return parser.parse_args()


def quick_export_to_excel(sql_query, output_path, sheet_name="数据"):
    """
    快速导出SQL查询结果到Excel文件
    
    Args:
        sql_query (str): SQL查询语句
        output_path (str): 输出Excel文件路径
        sheet_name (str): Excel工作表名称
    
    Returns:
        bool: 导出是否成功
    """
    try:
        print(f"正在连接数据库...")
        
        # 连接数据库
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset']
        )
        
        print(f"数据库连接成功")
        print(f"正在执行SQL查询...")
        
        # 执行查询
        df = pd.read_sql(sql_query, connection)
        
        if df.empty:
            print("警告: 查询结果为空")
            return False
        
        print(f"查询成功，获取到 {len(df)} 行数据")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        
        # 导出到Excel
        print(f"正在导出到Excel文件: {output_path}")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✅ 导出成功！")
        print(f"📊 数据统计: {len(df)} 行, {len(df.columns)} 列")
        print(f"📁 文件位置: {output_path}")
        
        # 关闭数据库连接
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False


def show_available_queries():
    """显示所有可用的查询"""
    print("\n📋 可用的SQL查询:")
    print("=" * 50)
    
    queries = list_queries()
    if not queries:
        print("❌ 没有找到可用的SQL查询")
        return
    
    for i, (query_name, description) in enumerate(queries.items(), 1):
        print(f"{i:2d}. {query_name}")
        print(f"    {description}")
        print()


def export_by_query_name(query_name, output_path, sheet_name=None, **params):
    """
    通过查询名称导出数据
    
    Args:
        query_name (str): 查询名称
        output_path (str): 输出路径
        sheet_name (str): 工作表名称
        **params: 查询参数
    """
    # 获取SQL查询
    if params:
        sql_query = format_query(query_name, **params)
    else:
        sql_query = get_query(query_name)
    
    if not sql_query:
        print(f"❌ 查询 '{query_name}' 不存在或参数错误")
        return False
    
    # 设置默认工作表名称
    if not sheet_name:
        sheet_name = query_name
    
    print(f"📝 使用查询: {query_name}")
    if params:
        print(f"📋 参数: {params}")
    
    return quick_export_to_excel(sql_query, output_path, sheet_name)


def main():
    """主函数 - 支持命令行参数和交互式配置"""
    
    # 优先支持命令行参数
    args = parse_cmd_args()
    if args.query:
        query_name = args.query
        params = {}
        for p in args.params:
            if '=' in p:
                k, v = p.split('=', 1)
                params[k] = v
        
        # 设置默认输出路径
        if args.output:
            output_path = args.output
        else:
            output_dir = r"E:\DOCUMENTS\inbox\new MySQL\data\exports"
            output_path = os.path.join(output_dir, f"{query_name}.xlsx")
        
        sheet_name = args.sheet or query_name
        
        print("🚀 开始数据库导出...")
        print(f"📝 命令行参数调用: {query_name}")
        print(f"📋 参数: {params}")
        print(f"📂 输出路径: {output_path}")
        print("-" * 50)
        
        success = export_by_query_name(query_name, output_path, sheet_name, **params)
        if success:
            print("-" * 50)
            print("🎉 导出完成！")
        else:
            print("-" * 50)
            print("💥 导出失败，请检查错误信息")
        return

    # ========== 交互式配置（原有逻辑）==========
    
    # 方式1: 直接使用SQL查询名称（推荐）
    USE_QUERY_NAME = True  # 设置为True使用查询名称，False使用直接SQL
    
    if USE_QUERY_NAME:
        # 查询名称（从sql_queries目录中的文件加载）
        query_name = "get_all_customers"  # 可用的查询名称
        
        # 查询参数（如果需要）
        params = {
            # 'start_date': '2024-01-01',
            # 'end_date': '2024-12-31',
            # 'min_amount': 1000
        }
        
        # 输出配置
        output_path = r"E:\DOCUMENTS\inbox\new MySQL\data\exports\客户数据.xlsx"
        sheet_name = "客户信息"
        
    else:
        # 方式2: 直接写SQL查询（传统方式）
        sql_query = """
        SELECT 
            order_id,
            customer_name,
            order_date,
            total_amount,
            status
        FROM new_customer_orders 
        WHERE order_date >= '2024-01-01'
        ORDER BY order_date DESC
        LIMIT 1000
        """
        
        output_path = r"E:\DOCUMENTS\inbox\new MySQL\data\exports\订单数据.xlsx"
        sheet_name = "订单数据"
    
    # ========== 配置完成 ==========
    
    print("🚀 开始数据库导出...")
    
    # 显示可用的查询
    show_available_queries()
    
    if USE_QUERY_NAME:
        print(f"📝 使用查询名称: {query_name}")
        success = export_by_query_name(query_name, output_path, sheet_name, **params)
    else:
        print(f"📝 使用直接SQL查询")
        success = quick_export_to_excel(sql_query, output_path, sheet_name)
    
    if success:
        print("-" * 50)
        print("🎉 导出完成！")
    else:
        print("-" * 50)
        print("💥 导出失败，请检查错误信息")


if __name__ == "__main__":
    main() 