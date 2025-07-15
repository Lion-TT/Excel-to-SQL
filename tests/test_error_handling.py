#!/usr/bin/env python3
"""
测试错误处理改进的脚本
"""

import os
import tempfile
import shutil
from src.importers.main_importer import get_excel_files

def test_excel_file_filtering():
    """测试Excel文件过滤功能"""
    
    print("=" * 60)
    print("测试Excel文件过滤功能")
    print("=" * 60)
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_files = [
            "normal_file.xlsx",
            "~$temp_file.xlsx",  # Excel临时文件
            "another_file.xls",
            "~$another_temp.xls",  # Excel临时文件
            "text_file.txt",  # 非Excel文件
            "~$locked_file.xlsx"  # 锁定的临时文件
        ]
        
        for file in test_files:
            file_path = os.path.join(temp_dir, file)
            with open(file_path, 'w') as f:
                f.write("test content")
        
        print(f"临时目录: {temp_dir}")
        print(f"创建的文件: {os.listdir(temp_dir)}")
        
        # 模拟get_excel_files函数
        def mock_get_excel_files():
            files = [f for f in os.listdir(temp_dir) 
                    if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
            return files
        
        filtered_files = mock_get_excel_files()
        
        print(f"\n过滤后的Excel文件: {filtered_files}")
        print(f"应该包含: normal_file.xlsx, another_file.xls")
        print(f"应该排除: ~$temp_file.xlsx, ~$another_temp.xls, ~$locked_file.xlsx, text_file.txt")

def test_error_classification():
    """测试错误分类逻辑"""
    
    print("\n" + "=" * 60)
    print("测试错误分类逻辑")
    print("=" * 60)
    
    test_errors = [
        ("PermissionError", "Permission denied", "非致命错误 - 应继续处理"),
        ("MemoryError", "Out of memory", "致命错误 - 应停止处理"),
        ("ValueError", "Invalid data", "非致命错误 - 应继续处理"),
        ("OSError", "File not found", "致命错误 - 应停止处理"),
        ("Exception", "Database unavailable", "致命错误 - 应停止处理"),
        ("Exception", "Unknown error", "非致命错误 - 应继续处理")
    ]
    
    for error_type, error_msg, expected_action in test_errors:
        print(f"\n错误类型: {error_type}")
        print(f"错误信息: {error_msg}")
        print(f"预期行为: {expected_action}")
        
        # 模拟错误分类逻辑
        if error_type in ["MemoryError", "OSError"] or "数据库不可用" in error_msg:
            print("  → 分类为: 致命错误")
        elif error_type == "PermissionError" or "Permission denied" in error_msg:
            print("  → 分类为: 权限错误 (跳过当前任务)")
        else:
            print("  → 分类为: 非致命错误 (继续处理)")

def test_task_completion_tracking():
    """测试任务完成跟踪"""
    
    print("\n" + "=" * 60)
    print("测试任务完成跟踪")
    print("=" * 60)
    
    # 模拟4个任务的处理结果
    task_results = [
        ("拜访记录.xlsx", "SUCCESS", "50000行数据"),
        ("~$新客处理.xlsx", "PERMISSION_ERROR", "文件被锁定"),
        ("销售订单.xlsx", "SUCCESS", "19716行数据"),
        ("新客处理.xlsx", "SUCCESS", "27075行数据")
    ]
    
    completed = 0
    failed = 0
    
    for i, (filename, status, details) in enumerate(task_results, 1):
        print(f"\n任务 {i}: {filename}")
        print(f"状态: {status}")
        print(f"详情: {details}")
        
        if status == "SUCCESS":
            completed += 1
            print("  → 任务成功完成")
        else:
            failed += 1
            print("  → 任务失败，但不影响其他任务")
    
    print(f"\n总结:")
    print(f"成功任务: {completed}/4")
    print(f"失败任务: {failed}/4")
    print(f"成功率: {completed/4*100:.1f}%")

if __name__ == "__main__":
    test_excel_file_filtering()
    test_error_classification()
    test_task_completion_tracking() 