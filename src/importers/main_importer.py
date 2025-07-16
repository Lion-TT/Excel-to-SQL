import os
import sys
import argparse
import time
import traceback
from datetime import datetime
import logging
from typing import Optional, Tuple, List
from src.importers.xlsx_to_csv import convert_excel_to_csv_by_schema
from src.importers.db_importer import import_table, import_dataframe_to_mysql, truncate_table
from src.shared.table_schemas import TABLE_SCHEMAS
from src.shared.config import DATA_SOURCES, get_excel_dir, get_csv_dir_for_table, BATCH_GROUPS, TABLE_COLUMNS, get_update_strategy
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, Future
import queue
import threading
from src.importers.db_importer import engine


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 全局常量
FILE_SIZE_TIMEOUT_MAPPING = {
    'small': 300, 'medium': 1800, 'large': 3600, 'huge': 7200
}

class ConcurrentExcelImporter:
    """
    通过管理生产者和消费者线程池，并发地处理和导入Excel文件。
    """
    def __init__(self, max_producers: int = 4, max_consumers: int = 4):
        self.max_producers = max_producers
        self.max_consumers = max_consumers
        self.dataframe_queue = queue.Queue(maxsize=20)
        self.error_queue = queue.Queue()
        self.pending_tasks = queue.Queue()
        self.should_stop = threading.Event()
        self.all_tasks_submitted = threading.Event()
        self.producer_executor = ThreadPoolExecutor(max_workers=self.max_producers, thread_name_prefix='Producer')
        self.consumer_executor = ThreadPoolExecutor(max_workers=self.max_consumers, thread_name_prefix='Consumer')
        self.table_locks = {}
        # 新增: 用于确保truncate操作只执行一次的锁和集合
        self._truncate_once_lock = threading.Lock()
        self._truncated_tables = set()

    def log_progress(self, message: str, level: str = "INFO"):
        logger.log(getattr(logging, level.upper()), message)

    def _get_excel_files(self, table_name: str) -> list:
        excel_dir = get_excel_dir(table_name)
        if not os.path.exists(excel_dir): return []
        return [f for f in os.listdir(excel_dir) if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')]

    def _get_dynamic_timeout(self, file_path: str) -> int:
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb < 50: category = 'small'
            elif size_mb < 200: category = 'medium'
            elif size_mb < 500: category = 'large'
            else: category = 'huge'
        except:
            category = 'medium'
        return int(max(FILE_SIZE_TIMEOUT_MAPPING[category], size_mb * 3))

    def _validate_dataframe(self, df: pd.DataFrame, table_name: str) -> Tuple[bool, str]:
        schema = TABLE_SCHEMAS.get(table_name, {})
        required_cols = [col[0] for col in schema.get('columns', [])]
        missing = set(required_cols) - set(df.columns)
        if missing: return False, f"缺少列: {', '.join(missing)}"
        if df.empty: return False, "数据为空"
        return True, "验证通过"

    def _producer_task(self, excel_path: str, table_name: str):
        try:
            if self.should_stop.is_set(): return
            self.log_progress(f"开始处理: {os.path.basename(excel_path)}")
            df = pd.read_excel(excel_path, dtype=str)
            
            # 根据 schema 过滤列
            required_cols = TABLE_COLUMNS.get(table_name)
            if required_cols:
                # 只保留 schema 中定义的列，忽略 Excel 中多余的列
                existing_cols = [col for col in required_cols if col in df.columns]
                df = df[existing_cols]
                if len(existing_cols) != len(required_cols):
                    self.log_progress(f"警告: 文件 {os.path.basename(excel_path)} 缺少以下列: {set(required_cols) - set(existing_cols)}", "WARNING")

            # 针对 'customer_info' 表的特殊数据清洗逻辑
            if table_name == 'customer_info':
                if '首单时间' in df.columns:
                    # 将无效日期（如 NaT, None, ''）统一替换为 '2000-01-01'
                    df['首单时间'] = pd.to_datetime(df['首单时间'], errors='coerce').fillna(datetime(2000, 1, 1)).dt.strftime('%Y-%m-%d')
                    self.log_progress(f"已对 'customer_info' 表的 '首单时间' 进行特殊处理", "DEBUG")

            pk = TABLE_SCHEMAS.get(table_name, {}).get('primary_key')
            if pk and pk in df.columns and df.duplicated(subset=[pk]).any():
                df.drop_duplicates(subset=[pk], keep='first', inplace=True)
                self.log_progress(f"主键重复数据已去重", "WARNING")

            if df.empty:
                self.log_progress(f"去重后数据为空，跳过", "WARNING")
                return
            
            is_valid, msg = self._validate_dataframe(df, table_name)
            if not is_valid: raise ValueError(f"数据验证失败: {msg}")

            self.pending_tasks.put(1)
            self.dataframe_queue.put((df, table_name), timeout=self._get_dynamic_timeout(excel_path))
            self.log_progress(f"已放入队列: {os.path.basename(excel_path)}", "DEBUG")
        except Exception as e:
            self.error_queue.put(f"处理 '{excel_path}' 失败: {e}")
            self.log_progress(f"处理 '{excel_path}' 失败: {e}\n{traceback.format_exc()}", "ERROR")
            if isinstance(e, MemoryError): self.should_stop.set()

    def _consumer_task(self):
        while not self.should_stop.is_set():
            try:
                df, table_name = self.dataframe_queue.get(timeout=1)
                
                # --- 新增: "只清空一次" 逻辑 ---
                update_strategy = get_update_strategy(table_name)
                if update_strategy == 'truncate':
                    with self._truncate_once_lock:
                        if table_name not in self._truncated_tables:
                            try:
                                self.log_progress(f"检测到 'truncate' 策略，首次任务将清空表: {table_name}")
                                truncate_table(table_name, engine)
                                self._truncated_tables.add(table_name)
                            except Exception as e:
                                self.log_progress(f"清空表 {table_name} 失败: {e}", "ERROR")
                                self.error_queue.put(f"清空表 {table_name} 失败: {e}")
                                # 如果清空失败，应该停止后续所有操作
                                self.should_stop.set()
                                self.dataframe_queue.task_done()
                                self.pending_tasks.get()
                                continue
                # --- 逻辑结束 ---

                lock = self.table_locks.get(table_name)
                if not lock:
                    self.log_progress(f"警告: 未找到表 '{table_name}' 的锁，跳过此任务。", "WARNING")
                    self.dataframe_queue.task_done()
                    self.pending_tasks.get()
                    continue
                
                with lock:
                    self.log_progress(f"开始导入 '{table_name}' ({len(df)}行)")
                    import_dataframe_to_mysql(df, table_name)
                    self.log_progress(f"成功导入 '{table_name}'")
                
                self.dataframe_queue.task_done()
                self.pending_tasks.get()
            except queue.Empty:
                if self.all_tasks_submitted.is_set() and self.pending_tasks.empty():
                    break
            except Exception as e:
                self.error_queue.put(f"导入 '{table_name}' 失败: {e}")
                self.log_progress(f"导入 '{table_name}' 失败: {e}\n{traceback.format_exc()}", "ERROR")
                if "MySQL server has gone away" in str(e): self.should_stop.set()

    def run(self, target_tables: List[str]):
        start_time = time.time()
        self.log_progress(f"开始执行 (P: {self.max_producers}, C: {self.max_consumers})...")
        
        for table in target_tables: self.table_locks[table] = threading.Lock()

        consumer_futures = [self.consumer_executor.submit(self._consumer_task) for _ in range(self.max_consumers)]
        producer_futures = []
        for table in target_tables:
            if self.should_stop.is_set(): break
            for file in self._get_excel_files(table):
                path = os.path.join(get_excel_dir(table), file)
                producer_futures.append(self.producer_executor.submit(self._producer_task, path, table))

        self.log_progress("所有生产者任务已提交。")
        for future in producer_futures: future.result() # 等待生产者完成
        
        self.all_tasks_submitted.set()
        self.log_progress("所有生产者任务完成，等待消费者...")
        for future in consumer_futures: future.result() # 等待消费者完成

        self.log_progress("所有任务完成。")
        self.producer_executor.shutdown()
        self.consumer_executor.shutdown()
        
        end_time = time.time()
        self.log_progress(f"批量导入任务结束，总耗时: {end_time - start_time:.2f} 秒。")
        
        if not self.error_queue.empty():
            self.log_progress("检测到以下错误:", "ERROR")
            while not self.error_queue.empty(): logger.error(f"- {self.error_queue.get()}")
            sys.exit(1)
        
        self.log_progress("任务成功完成，没有发生错误。")

def main():
    parser = argparse.ArgumentParser(description="MySQL 数据并发导入工具")
    parser.add_argument('--group', help='要导入的批处理组名')
    parser.add_argument('table_names', nargs='*', help='要导入的表名')
    args = parser.parse_args()

    if args.group:
        target_tables = BATCH_GROUPS.get(args.group, [])
    elif args.table_names:
        target_tables = args.table_names
    else:
        target_tables = list(TABLE_SCHEMAS.keys())

    if not target_tables:
        print("未找到需要导入的表，请检查参数。")
        return

    importer = ConcurrentExcelImporter(max_producers=4, max_consumers=4)
    try:
        importer.run(target_tables)
    except Exception as e:
        logger.critical(f"发生未捕获的严重错误: {e}\n{traceback.format_exc()}")
        importer.should_stop.set()
        sys.exit(1)

if __name__ == '__main__':
    main() 