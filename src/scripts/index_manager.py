#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引管理工具
用于查看、创建、删除数据库索引
"""

import sys
import os
import argparse
import logging
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.shared.config import get_database_connection
from src.shared.table_schemas import (
    TABLE_SCHEMAS, 
    get_table_indexes, 
    get_index_by_name,
    get_indexes_by_type,
    get_indexes_by_column,
    generate_create_index_sql,
    generate_drop_index_sql,
    get_all_indexes_sql,
    validate_index_config,
    INDEX_TYPES
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('index_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IndexManager:
    """索引管理器"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = get_database_connection()
            self.cursor = self.connection.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("数据库连接已断开")
    
    def show_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """显示表的现有索引"""
        try:
            sql = """
            SELECT 
                INDEX_NAME,
                COLUMN_NAME,
                NON_UNIQUE,
                SEQ_IN_INDEX,
                INDEX_TYPE
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = %s
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """
            self.cursor.execute(sql, (table_name,))
            results = self.cursor.fetchall()
            
            indexes = {}
            for row in results:
                index_name, column_name, non_unique, seq_in_index, index_type = row
                if index_name not in indexes:
                    indexes[index_name] = {
                        'name': index_name,
                        'columns': [],
                        'is_unique': non_unique == 0,
                        'type': index_type
                    }
                indexes[index_name]['columns'].append(column_name)
            
            return list(indexes.values())
        except Exception as e:
            logger.error(f"查询表索引失败: {e}")
            return []
    
    def show_configured_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """显示配置文件中定义的索引"""
        return get_table_indexes(table_name)
    
    def create_index(self, table_name: str, index_name: str) -> bool:
        """创建指定索引"""
        try:
            index_info = get_index_by_name(table_name, index_name)
            if not index_info:
                logger.error(f"索引 {index_name} 在配置中不存在")
                return False
            
            sql = generate_create_index_sql(table_name, index_info)
            logger.info(f"执行SQL: {sql}")
            self.cursor.execute(sql)
            self.connection.commit()
            logger.info(f"索引 {index_name} 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
            self.connection.rollback()
            return False
    
    def drop_index(self, table_name: str, index_name: str) -> bool:
        """删除指定索引"""
        try:
            sql = generate_drop_index_sql(table_name, index_name)
            logger.info(f"执行SQL: {sql}")
            self.cursor.execute(sql)
            self.connection.commit()
            logger.info(f"索引 {index_name} 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除索引失败: {e}")
            self.connection.rollback()
            return False
    
    def create_all_indexes(self, table_name: str) -> bool:
        """创建表的所有配置索引"""
        try:
            indexes = get_table_indexes(table_name)
            if not indexes:
                logger.warning(f"表 {table_name} 没有配置索引")
                return True
            
            success_count = 0
            for index in indexes:
                if self.create_index(table_name, index['name']):
                    success_count += 1
            
            logger.info(f"表 {table_name} 索引创建完成: {success_count}/{len(indexes)} 成功")
            return success_count == len(indexes)
        except Exception as e:
            logger.error(f"创建所有索引失败: {e}")
            return False
    
    def compare_indexes(self, table_name: str) -> Dict[str, Any]:
        """比较配置的索引和实际的索引"""
        configured = self.show_configured_indexes(table_name)
        actual = self.show_table_indexes(table_name)
        
        configured_names = {idx['name'] for idx in configured}
        actual_names = {idx['name'] for idx in actual}
        
        missing = configured_names - actual_names
        extra = actual_names - configured_names
        common = configured_names & actual_names
        
        return {
            'missing': list(missing),
            'extra': list(extra),
            'common': list(common),
            'configured': configured,
            'actual': actual
        }
    
    def validate_table_indexes(self, table_name: str) -> bool:
        """验证表索引配置"""
        is_valid, errors = validate_index_config(table_name)
        if not is_valid:
            logger.error(f"表 {table_name} 索引配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info(f"表 {table_name} 索引配置验证通过")
        return is_valid

def print_index_info(indexes: List[Dict[str, Any]], title: str):
    """打印索引信息"""
    print(f"\n{title}:")
    print("=" * 60)
    if not indexes:
        print("  无索引")
        return
    
    for index in indexes:
        unique_flag = "唯一" if index.get('is_unique', False) else "普通"
        columns_str = ", ".join(index['columns'])
        print(f"  {index['name']} ({unique_flag})")
        print(f"    字段: {columns_str}")
        print(f"    类型: {index.get('type', 'BTREE')}")
        print()

def main():
    parser = argparse.ArgumentParser(description='数据库索引管理工具')
    parser.add_argument('action', choices=['list', 'show', 'create', 'drop', 'create-all', 'compare', 'validate'], 
                       help='操作类型')
    parser.add_argument('table', nargs='?', help='表名（list操作不需要）')
    parser.add_argument('--index', help='索引名称（用于create/drop操作）')
    parser.add_argument('--type', choices=list(INDEX_TYPES.keys()), help='索引类型过滤')
    parser.add_argument('--column', help='字段名过滤')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.action != 'list' and not args.table:
        print("错误: 除list操作外，其他操作都需要指定表名")
        return
    
    manager = IndexManager()
    
    try:
        if args.action != 'list':
            manager.connect()
        
        if args.action == 'list':
            # 列出所有表
            print("可用的表:")
            for table_name in TABLE_SCHEMAS.keys():
                print(f"  - {table_name}")
        
        elif args.action == 'show':
            # 显示索引
            if args.type:
                indexes = get_indexes_by_type(args.table, args.type)
                print_index_info(indexes, f"表 {args.table} 的 {args.type} 类型索引")
            elif args.column:
                indexes = get_indexes_by_column(args.table, args.column)
                print_index_info(indexes, f"表 {args.table} 包含字段 {args.column} 的索引")
            else:
                configured = manager.show_configured_indexes(args.table)
                actual = manager.show_table_indexes(args.table)
                print_index_info(configured, f"表 {args.table} 配置的索引")
                print_index_info(actual, f"表 {args.table} 实际的索引")
        
        elif args.action == 'create':
            if not args.index:
                print("错误: 创建索引需要指定 --index 参数")
                return
            manager.create_index(args.table, args.index)
        
        elif args.action == 'drop':
            if not args.index:
                print("错误: 删除索引需要指定 --index 参数")
                return
            manager.drop_index(args.table, args.index)
        
        elif args.action == 'create-all':
            manager.create_all_indexes(args.table)
        
        elif args.action == 'compare':
            result = manager.compare_indexes(args.table)
            print(f"\n表 {args.table} 索引比较结果:")
            print("=" * 60)
            print(f"缺失的索引: {result['missing']}")
            print(f"多余的索引: {result['extra']}")
            print(f"共同的索引: {result['common']}")
        
        elif args.action == 'validate':
            manager.validate_table_indexes(args.table)
    
    except Exception as e:
        logger.error(f"操作失败: {e}")
    finally:
        if args.action != 'list':
            manager.disconnect()

if __name__ == '__main__':
    main() 