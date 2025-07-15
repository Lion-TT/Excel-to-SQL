#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询管理器
用于加载和管理SQL查询文件
"""

import os
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SQLQueryManager:
    """SQL查询管理器"""
    
    def __init__(self, sql_dir: str = "sql_queries"):
        """
        初始化SQL查询管理器
        
        Args:
            sql_dir: SQL文件目录路径
        """
        self.sql_dir = sql_dir
        self.queries = {}
        self.load_all_queries()
    
    def load_all_queries(self):
        """加载所有SQL文件中的查询"""
        if not os.path.exists(self.sql_dir):
            logger.warning(f"SQL目录不存在: {self.sql_dir}")
            return
        
        for filename in os.listdir(self.sql_dir):
            if filename.endswith('.sql'):
                file_path = os.path.join(self.sql_dir, filename)
                self.load_queries_from_file(file_path)
    
    def load_queries_from_file(self, file_path: str):
        """从SQL文件中加载查询"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析SQL文件中的查询
            queries = self._parse_sql_file(content)
            
            # 添加到查询字典中
            for query_name, query_sql in queries.items():
                self.queries[query_name] = query_sql
                logger.info(f"加载查询: {query_name} (来自 {os.path.basename(file_path)})")
                
        except Exception as e:
            logger.error(f"加载SQL文件失败 {file_path}: {e}")
    
    def _parse_sql_file(self, content: str) -> Dict[str, str]:
        """
        解析SQL文件内容，提取查询
        
        Args:
            content: SQL文件内容
            
        Returns:
            Dict[str, str]: 查询名称到SQL语句的映射
        """
        queries = {}
        
        # 使用正则表达式匹配查询
        # 匹配格式: -- 使用: query_name 后面的SQL语句
        pattern = r'--\s*使用:\s*(\w+)\s*\n(.*?)(?=\n--\s*使用:|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for query_name, sql_content in matches:
            # 清理SQL内容
            sql = sql_content.strip()
            if sql:
                queries[query_name] = sql
        
        return queries
    
    def get_query(self, query_name: str) -> Optional[str]:
        """
        获取指定的查询
        
        Args:
            query_name: 查询名称
            
        Returns:
            str: SQL查询语句，如果不存在则返回None
        """
        return self.queries.get(query_name)
    
    def get_all_query_names(self) -> List[str]:
        """
        获取所有查询名称
        
        Returns:
            List[str]: 查询名称列表
        """
        return list(self.queries.keys())
    
    def format_query(self, query_name: str, **kwargs) -> Optional[str]:
        """
        格式化查询（替换参数）
        
        Args:
            query_name: 查询名称
            **kwargs: 参数值
            
        Returns:
            str: 格式化后的SQL查询语句
        """
        query = self.get_query(query_name)
        if query is None:
            logger.error(f"查询不存在: {query_name}")
            return None
        
        try:
            # 替换参数
            formatted_query = query.format(**kwargs)
            return formatted_query
        except KeyError as e:
            logger.error(f"查询参数缺失 {query_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"格式化查询失败 {query_name}: {e}")
            return None
    
    def list_queries(self) -> Dict[str, str]:
        """
        列出所有查询及其描述
        
        Returns:
            Dict[str, str]: 查询名称到描述的映射
        """
        result = {}
        for query_name in self.queries:
            # 获取查询的前几行作为描述
            query = self.queries[query_name]
            lines = query.strip().split('\n')
            description = lines[0] if lines else query_name
            result[query_name] = description
        
        return result
    
    def reload_queries(self):
        """重新加载所有查询"""
        self.queries.clear()
        self.load_all_queries()
        logger.info("重新加载所有SQL查询")


# 全局SQL管理器实例
_sql_manager = None

def get_sql_manager() -> SQLQueryManager:
    """获取全局SQL管理器实例"""
    global _sql_manager
    if _sql_manager is None:
        _sql_manager = SQLQueryManager()
    return _sql_manager

def get_query(query_name: str) -> Optional[str]:
    """获取查询"""
    return get_sql_manager().get_query(query_name)

def format_query(query_name: str, **kwargs) -> Optional[str]:
    """格式化查询"""
    return get_sql_manager().format_query(query_name, **kwargs)

def list_queries() -> Dict[str, str]:
    """列出所有查询"""
    return get_sql_manager().list_queries() 