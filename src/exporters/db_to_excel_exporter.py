#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库到Excel导出工具
支持自定义SQL查询，将结果导出为Excel文件
"""

import os
import sys
import pandas as pd
import pymysql
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.shared.config import DB_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_export.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseToExcelExporter:
    """数据库到Excel导出器"""
    
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        初始化导出器
        
        Args:
            db_config: 数据库配置字典，如果为None则使用默认配置
        """
        self.db_config = db_config or DB_CONFIG
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                port=self.db_config['port'],
                charset=self.db_config['charset'],
                autocommit=True
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def execute_query(self, sql: str) -> Optional[pd.DataFrame]:
        """
        执行SQL查询并返回DataFrame
        
        Args:
            sql: SQL查询语句
            
        Returns:
            pandas DataFrame 或 None（如果查询失败）
        """
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            logger.info(f"执行SQL查询: {sql[:100]}...")
            df = pd.read_sql(sql, self.connection)
            logger.info(f"查询成功，返回 {len(df)} 行数据")
            return df
        except Exception as e:
            logger.error(f"SQL查询执行失败: {e}")
            return None
    
    def export_to_excel(self, 
                       sql: str, 
                       output_path: str, 
                       sheet_name: str = "Sheet1",
                       include_timestamp: bool = True) -> bool:
        """
        将SQL查询结果导出到Excel文件
        
        Args:
            sql: SQL查询语句
            output_path: 输出Excel文件路径
            sheet_name: Excel工作表名称
            include_timestamp: 是否在文件名中包含时间戳
            
        Returns:
            bool: 导出是否成功
        """
        try:
            # 执行查询
            df = self.execute_query(sql)
            if df is None or df.empty:
                logger.warning("查询结果为空，无法导出")
                return False
            
            # 处理输出路径
            if include_timestamp:
                output_path = self._add_timestamp_to_path(output_path)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"创建输出目录: {output_dir}")
            
            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"数据已成功导出到: {output_path}")
            logger.info(f"导出数据统计: {len(df)} 行, {len(df.columns)} 列")
            
            return True
            
        except Exception as e:
            logger.error(f"导出到Excel失败: {e}")
            return False
    
    def export_multiple_queries(self, 
                               queries: Dict[str, str], 
                               output_path: str,
                               include_timestamp: bool = True) -> bool:
        """
        将多个SQL查询结果导出到同一个Excel文件的不同工作表
        
        Args:
            queries: 字典，格式为 {'sheet_name': 'sql_query'}
            output_path: 输出Excel文件路径
            include_timestamp: 是否在文件名中包含时间戳
            
        Returns:
            bool: 导出是否成功
        """
        try:
            # 处理输出路径
            if include_timestamp:
                output_path = self._add_timestamp_to_path(output_path)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"创建输出目录: {output_dir}")
            
            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, sql in queries.items():
                    logger.info(f"处理工作表: {sheet_name}")
                    df = self.execute_query(sql)
                    if df is not None and not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.info(f"工作表 '{sheet_name}' 导出完成: {len(df)} 行")
                    else:
                        logger.warning(f"工作表 '{sheet_name}' 查询结果为空")
            
            logger.info(f"多表数据已成功导出到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"多表导出失败: {e}")
            return False
    
    def _add_timestamp_to_path(self, file_path: str) -> str:
        """
        在文件路径中添加时间戳
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            str: 添加时间戳后的文件路径
        """
        name, ext = os.path.splitext(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}{ext}"
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


def main():
    """主函数 - 示例用法"""
    
    # 示例SQL查询
    sample_queries = {
        "客户订单": """
            SELECT 
                o.order_id,
                o.customer_name,
                o.order_date,
                o.total_amount,
                o.status
            FROM new_customer_orders o
            WHERE o.order_date >= '2024-01-01'
            ORDER BY o.order_date DESC
            LIMIT 1000
        """,
        
        "拜访记录": """
            SELECT 
                v.visit_id,
                v.customer_name,
                v.visit_date,
                v.visit_type,
                v.notes
            FROM visit_record v
            WHERE v.visit_date >= '2024-01-01'
            ORDER BY v.visit_date DESC
            LIMIT 500
        """,
        
        "客户信息": """
            SELECT 
                c.customer_id,
                c.customer_name,
                c.contact_phone,
                c.email,
                c.region,
                c.created_date
            FROM customer_info c
            ORDER BY c.created_date DESC
            LIMIT 2000
        """
    }
    
    # 输出路径配置
    output_dir = r"E:\DOCUMENTS\inbox\new MySQL\data\exports"
    single_output_path = os.path.join(output_dir, "single_query_export.xlsx")
    multi_output_path = os.path.join(output_dir, "multi_query_export.xlsx")
    
    # 使用上下文管理器确保连接正确关闭
    with DatabaseToExcelExporter() as exporter:
        
        # 示例1: 导出单个查询
        logger.info("=== 开始单查询导出 ===")
        single_sql = """
            SELECT 
                order_id,
                customer_name,
                order_date,
                total_amount
            FROM new_customer_orders 
            WHERE order_date >= '2024-01-01'
            ORDER BY order_date DESC
            LIMIT 100
        """
        
        success = exporter.export_to_excel(
            sql=single_sql,
            output_path=single_output_path,
            sheet_name="订单数据"
        )
        
        if success:
            logger.info("单查询导出成功！")
        else:
            logger.error("单查询导出失败！")
        
        # 示例2: 导出多个查询到不同工作表
        logger.info("=== 开始多查询导出 ===")
        success = exporter.export_multiple_queries(
            queries=sample_queries,
            output_path=multi_output_path
        )
        
        if success:
            logger.info("多查询导出成功！")
        else:
            logger.error("多查询导出失败！")


if __name__ == "__main__":
    main() 