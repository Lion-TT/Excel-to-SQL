#!/usr/bin/env python3
"""
测试超时改进效果的脚本
"""

import os
import time
from src.importers.main_importer import get_dynamic_timeout, get_file_size_category

def test_timeout_calculations():
    """测试不同文件大小的超时计算"""
    
    # 模拟不同大小的文件
    test_files = [
        ("small_file.xlsx", 25 * 1024 * 1024),    # 25MB
        ("medium_file.xlsx", 100 * 1024 * 1024),  # 100MB  
        ("large_file.xlsx", 300 * 1024 * 1024),   # 300MB
        ("huge_file.xlsx", 800 * 1024 * 1024),    # 800MB
    ]
    
    print("=" * 80)
    print("超时计算测试")
    print("=" * 80)
    
    for filename, size_bytes in test_files:
        # 创建临时文件来测试
        with open(filename, 'wb') as f:
            f.write(b'0' * size_bytes)
        
        try:
            category = get_file_size_category(filename)
            timeout = get_dynamic_timeout(filename)
            
            print(f"\n文件: {filename}")
            print(f"大小: {size_bytes / (1024*1024):.1f}MB")
            print(f"类别: {category}")
            print(f"超时时间: {timeout}秒 ({timeout/60:.1f}分钟)")
            
        finally:
            # 清理临时文件
            if os.path.exists(filename):
                os.remove(filename)

def test_actual_files():
    """测试实际文件的超时计算"""
    
    print("\n" + "=" * 80)
    print("实际文件测试")
    print("=" * 80)
    
    # 从您的日志中提取的实际文件信息
    actual_files = [
        ("销售订单明细看板_for销售-20250709-10_03_13-921-日期_下单时间-tiantao06.xlsx", 88.8),
        ("销售订单明细看板_for销售-20250709-10_03_48-943-日期_下单时间-tiantao06.xlsx", 142.2),
        ("销售订单明细看板_for销售-20250709-10_03_53-707-日期_下单时间-tiantao06.xlsx", 162.0),
    ]
    
    total_timeout = 0
    
    for filename, size_mb in actual_files:
        # 创建临时文件
        size_bytes = int(size_mb * 1024 * 1024)
        with open(filename, 'wb') as f:
            f.write(b'0' * size_bytes)
        
        try:
            category = get_file_size_category(filename)
            timeout = get_dynamic_timeout(filename)
            total_timeout += timeout
            
            print(f"\n文件: {filename}")
            print(f"大小: {size_mb:.1f}MB")
            print(f"类别: {category}")
            print(f"超时时间: {timeout}秒 ({timeout/60:.1f}分钟)")
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    print(f"\n总计超时时间: {total_timeout}秒 ({total_timeout/60:.1f}分钟)")
    print(f"预计总处理时间: 20分钟 (1200秒)")
    print(f"超时余量: {(total_timeout - 1200)/60:.1f}分钟")

if __name__ == "__main__":
    test_timeout_calculations()
    test_actual_files() 