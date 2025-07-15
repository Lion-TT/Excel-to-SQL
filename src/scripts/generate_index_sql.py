#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引SQL脚本生成器
根据表结构配置生成创建索引的SQL文件
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.shared.table_schemas import (
    TABLE_SCHEMAS,
    get_table_indexes,
    generate_create_index_sql,
    generate_drop_index_sql,
    get_all_indexes_sql,
    validate_index_config
)

def generate_index_sql_file(table_name: str, output_dir: str = "sql_scripts") -> str:
    """为指定表生成索引SQL文件"""
    
    # 验证表配置
    is_valid, errors = validate_index_config(table_name)
    if not is_valid:
        print(f"表 {table_name} 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return None
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{table_name}_indexes_{timestamp}.sql"
    filepath = os.path.join(output_dir, filename)
    
    # 获取索引信息
    indexes = get_table_indexes(table_name)
    if not indexes:
        print(f"表 {table_name} 没有配置索引")
        return None
    
    # 生成SQL内容
    sql_content = []
    sql_content.append(f"-- {table_name} 表索引创建脚本")
    sql_content.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append(f"-- 表名: {table_name}")
    sql_content.append(f"-- 索引数量: {len(indexes)}")
    sql_content.append("")
    
    # 添加使用数据库语句
    sql_content.append("-- 使用数据库")
    sql_content.append("USE `your_database_name`;")
    sql_content.append("")
    
    # 添加索引创建语句
    sql_content.append("-- 创建索引")
    for index in indexes:
        sql_content.append(f"-- {index['name']}: {', '.join(index['columns'])} ({index['type']})")
        sql_content.append(generate_create_index_sql(table_name, index))
        sql_content.append("")
    
    # 添加索引删除语句（注释形式）
    sql_content.append("-- 删除索引语句（如需删除请取消注释）")
    for index in indexes:
        sql_content.append(f"-- {generate_drop_index_sql(table_name, index['name'])}")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_content))
    
    print(f"索引SQL文件已生成: {filepath}")
    print(f"包含 {len(indexes)} 个索引")
    
    return filepath

def generate_all_indexes_sql(output_dir: str = "sql_scripts") -> str:
    """为所有表生成索引SQL文件"""
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_tables_indexes_{timestamp}.sql"
    filepath = os.path.join(output_dir, filename)
    
    # 生成SQL内容
    sql_content = []
    sql_content.append("-- 所有表索引创建脚本")
    sql_content.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append(f"-- 表数量: {len(TABLE_SCHEMAS)}")
    sql_content.append("")
    
    # 添加使用数据库语句
    sql_content.append("-- 使用数据库")
    sql_content.append("USE `your_database_name`;")
    sql_content.append("")
    
    total_indexes = 0
    
    # 为每个表生成索引
    for table_name in TABLE_SCHEMAS.keys():
        # 验证表配置
        is_valid, errors = validate_index_config(table_name)
        if not is_valid:
            sql_content.append(f"-- 表 {table_name} 配置验证失败，跳过")
            for error in errors:
                sql_content.append(f"--   - {error}")
            sql_content.append("")
            continue
        
        indexes = get_table_indexes(table_name)
        if not indexes:
            sql_content.append(f"-- 表 {table_name} 没有配置索引")
            sql_content.append("")
            continue
        
        sql_content.append(f"-- ========================================")
        sql_content.append(f"-- 表: {table_name}")
        sql_content.append(f"-- 索引数量: {len(indexes)}")
        sql_content.append(f"-- ========================================")
        sql_content.append("")
        
        for index in indexes:
            sql_content.append(f"-- {index['name']}: {', '.join(index['columns'])} ({index['type']})")
            sql_content.append(generate_create_index_sql(table_name, index))
            sql_content.append("")
        
        total_indexes += len(indexes)
    
    sql_content.append(f"-- 总计: {total_indexes} 个索引")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_content))
    
    print(f"所有表索引SQL文件已生成: {filepath}")
    print(f"包含 {len(TABLE_SCHEMAS)} 个表，{total_indexes} 个索引")
    
    return filepath

def generate_index_report(output_dir: str = "reports") -> str:
    """生成索引配置报告"""
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"index_report_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # 生成报告内容
    report_content = []
    report_content.append("数据库索引配置报告")
    report_content.append("=" * 50)
    report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append(f"表数量: {len(TABLE_SCHEMAS)}")
    report_content.append("")
    
    total_indexes = 0
    index_types = {}
    
    for table_name in TABLE_SCHEMAS.keys():
        report_content.append(f"表: {table_name}")
        report_content.append("-" * 30)
        
        # 验证表配置
        is_valid, errors = validate_index_config(table_name)
        if not is_valid:
            report_content.append("状态: 配置错误")
            for error in errors:
                report_content.append(f"  错误: {error}")
            report_content.append("")
            continue
        
        indexes = get_table_indexes(table_name)
        if not indexes:
            report_content.append("状态: 无索引配置")
            report_content.append("")
            continue
        
        report_content.append(f"状态: 正常")
        report_content.append(f"索引数量: {len(indexes)}")
        report_content.append("索引详情:")
        
        for index in indexes:
            index_type = index['type']
            index_types[index_type] = index_types.get(index_type, 0) + 1
            
            report_content.append(f"  - {index['name']}")
            report_content.append(f"    字段: {', '.join(index['columns'])}")
            report_content.append(f"    类型: {index_type}")
            report_content.append("")
        
        total_indexes += len(indexes)
    
    # 统计信息
    report_content.append("统计信息")
    report_content.append("=" * 30)
    report_content.append(f"总索引数: {total_indexes}")
    for index_type, count in index_types.items():
        report_content.append(f"{index_type} 类型: {count}")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"索引配置报告已生成: {filepath}")
    
    return filepath

def main():
    parser = argparse.ArgumentParser(description='索引SQL脚本生成器')
    parser.add_argument('action', choices=['table', 'all', 'report'], 
                       help='生成类型: table(单表), all(所有表), report(报告)')
    parser.add_argument('--table', help='表名（用于table操作）')
    parser.add_argument('--output-dir', default='sql_scripts', help='输出目录')
    parser.add_argument('--report-dir', default='reports', help='报告输出目录')
    
    args = parser.parse_args()
    
    if args.action == 'table':
        if not args.table:
            print("错误: 单表生成需要指定 --table 参数")
            return
        
        if args.table not in TABLE_SCHEMAS:
            print(f"错误: 表 {args.table} 不存在")
            print("可用的表:")
            for table_name in TABLE_SCHEMAS.keys():
                print(f"  - {table_name}")
            return
        
        generate_index_sql_file(args.table, args.output_dir)
    
    elif args.action == 'all':
        generate_all_indexes_sql(args.output_dir)
    
    elif args.action == 'report':
        generate_index_report(args.report_dir)

if __name__ == '__main__':
    main() 