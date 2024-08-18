import pandas as pd
import ctypes
import time

def get_system_memory_info():
    """시스템 메모리 정보를 MB 단위로 반환하는 함수"""
    kernel32 = ctypes.windll.kernel32
    c_ulonglong = ctypes.c_ulonglong

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_uint),
                    ("dwMemoryLoad", ctypes.c_uint),
                    ("ullTotalPhys", c_ulonglong),
                    ("ullAvailPhys", c_ulonglong),
                    ("ullTotalPageFile", c_ulonglong),
                    ("ullAvailPageFile", c_ulonglong),
                    ("ullTotalVirtual", c_ulonglong),
                    ("ullAvailVirtual", c_ulonglong),
                    ("sullAvailExtendedVirtual", c_ulonglong),]

    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))

    available_memory_mb = memory_status.ullAvailPhys / (1024 * 1024)  # MB 단위로 변환
    return available_memory_mb

def calculate_dynamic_chunksize(last_memory_check_time, cached_chunksize, base_chunksize=10000, cache_duration=20):
    """시스템 메모리 정보를 기반으로 동적으로 chunksize를 계산하는 함수"""
    current_time = time.time()
    if cached_chunksize and (current_time - last_memory_check_time) < cache_duration:
        return cached_chunksize, last_memory_check_time  # 캐시된 chunksize 값을 반환

    available_memory_mb = get_system_memory_info()
    target_memory_usage_mb = available_memory_mb * 0.05
    estimated_memory_per_row_mb = 0.001

    calculated_chunksize = int(target_memory_usage_mb / estimated_memory_per_row_mb)
    cached_chunksize = min(max(base_chunksize, calculated_chunksize), 1000000)
    last_memory_check_time = current_time
    return cached_chunksize, last_memory_check_time

def load_csv_with_chunksize(file_name, chunksize):
    """동적으로 계산된 chunksize를 사용하여 CSV 파일을 로드하는 함수"""
    chunks = pd.read_csv(file_name, chunksize=chunksize)
    df = pd.concat(chunk for chunk in chunks)
    return df
