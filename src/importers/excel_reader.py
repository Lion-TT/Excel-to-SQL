# excel_reader.py
# 用于批量读取CSV文件的模块
import os
import pandas as pd
from src.shared.config import EXCEL_DIR

def get_csv_files(directory: str) -> list:
    """
    获取指定目录下所有有效的CSV文件路径列表。
    - 只包含 .csv 文件。
    - 如果目录不存在或为空，返回空列表。
    """
    if not os.path.isdir(directory):
        print(f"警告：目录 '{directory}' 不存在。")
        return []
    csv_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.csv'):
            csv_files.append(os.path.join(directory, filename))
    if not csv_files:
        print(f"提示：在目录 '{directory}' 中没有找到CSV文件。")
    return csv_files

def read_csv_by_chunks(file_path: str, chunk_size: int = 20000):
    """
    以分块的方式读取大型CSV文件，以节省内存。
    Args:
        file_path (str): CSV文件的路径。
        chunk_size (int, optional): 每个数据块的行数。默认为20000。
    Yields:
        DataFrame: CSV文件中的一个数据块（pandas DataFrame）。
    """
    print(f"正在以每块 {chunk_size} 行的方式，分块读取文件: {os.path.basename(file_path)}")
    try:
        reader = pd.read_csv(file_path, chunksize=chunk_size, encoding='gbk')
        for chunk in reader:
            yield chunk
    except FileNotFoundError:
        print(f"错误：文件未找到 - {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误 {file_path}: {e}")

# --- 模块自测试代码 ---
if __name__ == '__main__':
    print(f"--- 开始测试CSV文件读取模块 ---")
    print(f"Pandas 版本: {pd.__version__}")
    # 1. 获取所有CSV文件列表
    all_files = get_csv_files(EXCEL_DIR)
    if all_files:
        print(f"\n成功在指定目录中找到以下 {len(all_files)} 个CSV文件:")
        for f in all_files:
            print(f"- {os.path.basename(f)}")
        # 2. 测试分块读取第一个文件
        print("\n--- 测试分块读取第一个文件 ---")
        first_file = all_files[0]
        chunk_iterator = read_csv_by_chunks(first_file)
        try:
            first_chunk = next(chunk_iterator)
            print(f"成功读取到第一个数据块，包含 {len(first_chunk)} 行数据。")
            print("数据的前5行是:")
            print(first_chunk.head())
        except StopIteration:
            print("文件为空或无法读取。")
        except Exception as e:
            print(f"处理第一个数据块时出错: {e}")
    else:
        print("\n未找到任何CSV文件，测试结束。")
    print("\n--- CSV文件读取模块测试结束 ---") 