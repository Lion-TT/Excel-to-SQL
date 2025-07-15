#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量数据库导出工具
支持从SQL文件批量导出多个查询到Excel
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.exporters.db_to_excel_exporter import DatabaseToExcelExporter
from src.exporters.sql_manager import get_query, format_query, list_queries


def batch_export_queries(export_configs, output_dir, include_timestamp=True):
    """
    批量导出多个查询
    
    Args:
        export_configs: 导出配置列表，每个配置包含查询名称、参数、输出文件名等
        output_dir: 输出目录
        include_timestamp: 是否在文件名中添加时间戳
    """
    print("🚀 开始批量导出...")
    print(f"📂 输出目录: {output_dir}")
    print(f"📋 导出任务数: {len(export_configs)}")
    print("=" * 60)
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 创建输出目录: {output_dir}")
    
    success_count = 0
    failed_count = 0
    
    with DatabaseToExcelExporter() as exporter:
        for i, config in enumerate(export_configs, 1):
            query_name = config['query_name']
            sheet_name = config.get('sheet_name', query_name)
            params = config.get('params', {})
            
            print(f"\n📊 任务 {i}/{len(export_configs)}: {query_name}")
            print(f"📝 查询名称: {query_name}")
            if params:
                print(f"📋 参数: {params}")
            
            # 优先用 output_filename，否则用默认
            if 'output_filename' in config and config['output_filename']:
                output_path = os.path.join(output_dir, config['output_filename'])
                print(f"📁 指定输出文件: {config['output_filename']}")
            else:
                output_path = os.path.join(output_dir, f"{query_name}.xlsx")
                print(f"📁 使用默认文件名: {query_name}.xlsx")
            
            # 获取SQL查询
            if params:
                sql_query = format_query(query_name, **params)
            else:
                sql_query = get_query(query_name)
            
            if not sql_query:
                print(f"❌ 查询 '{query_name}' 不存在或参数错误")
                failed_count += 1
                continue
            
            # 执行导出
            success = exporter.export_to_excel(
                sql=sql_query,
                output_path=output_path,
                sheet_name=sheet_name,
                include_timestamp=include_timestamp
            )
            
            if success:
                print(f"✅ 导出成功: {os.path.basename(output_path)}")
                success_count += 1
            else:
                print(f"❌ 导出失败: {os.path.basename(output_path)}")
                failed_count += 1
    
    print("\n" + "=" * 60)
    print("📊 批量导出完成！")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")
    
    return success_count, failed_count


def main():
    """主函数 - 配置批量导出任务"""
    
    # ========== 批量导出配置 ==========
    
    # 输出目录
    output_dir = r"E:\DOCUMENTS\inbox\new MySQL\data\exports\batch_export"
    
    # 导出配置列表
    export_configs = [
        {
            'query_name': 'get_all_customers',
            'sheet_name': '客户信息',
            'params': {}
            # 不指定 output_filename，自动用 get_all_customers.xlsx
        },
        {
            'query_name': 'get_all_orders',
            'output_filename': '订单信息汇总.xlsx',  # 指定输出文件名
            'sheet_name': '订单信息',
            'params': {}
        },
        {
            'query_name': 'get_orders_by_date_range',
            'output_filename': '2024年上半年订单.xlsx',  # 指定输出文件名
            'sheet_name': '近期订单',
            'params': {
                'start_date': '2024-01-01',
                'end_date': '2024-06-30'
            }
        },
        {
            'query_name': 'get_customer_order_summary',
            'sheet_name': '客户汇总',
            'params': {
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'min_amount': 1000
            }
            # 不指定 output_filename，自动用 get_customer_order_summary.xlsx
        },
        {
            'query_name': 'get_all_visits',
            'output_filename': '拜访记录统计.xlsx',  # 指定输出文件名
            'sheet_name': '拜访记录',
            'params': {}
        },
        {
            'query_name': 'get_monthly_sales_stats',
            'output_filename': '2024年销售月度统计.xlsx',  # 指定输出文件名
            'sheet_name': '月度统计',
            'params': {
                'start_date': '2024-01-01',
                'end_date': '2024-12-31'
            }
        }
    ]
    
    # ========== 配置完成 ==========
    
    # 显示可用的查询
    print("📋 可用的SQL查询:")
    print("=" * 50)
    queries = list_queries()
    for query_name, description in queries.items():
        print(f"  • {query_name}: {description}")
    
    print(f"\n📊 准备导出 {len(export_configs)} 个查询:")
    for config in export_configs:
        query_name = config['query_name']
        output_filename = config.get('output_filename', f"{query_name}.xlsx")
        print(f"  • {query_name} -> {output_filename}")
    
    # 执行批量导出
    success_count, failed_count = batch_export_queries(
        export_configs=export_configs,
        output_dir=output_dir,
        include_timestamp=True
    )
    
    if failed_count == 0:
        print("\n🎉 所有任务导出成功！")
    else:
        print(f"\n⚠️ 有 {failed_count} 个任务失败，请检查错误信息")


if __name__ == "__main__":
    main() 