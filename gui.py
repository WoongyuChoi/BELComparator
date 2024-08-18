import pandas as pd
import ctypes
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from bel_comparator import BELComparator
from custom_exceptions import MissingColumnsError, InvalidBELValuesError

class BELComparatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.inno_csv_path = None  # Innolink CSV 파일 경로를 저장할 변수
        self.pw_csv_path = None  # Pathwise CSV 파일 경로를 저장할 변수
        self.sort_order = Qt.AscendingOrder  # 초기 정렬 순서 설정
        self.last_memory_check_time = 0  # 마지막 메모리 체크 시간을 저장할 변수
        self.cached_chunksize = None  # 캐시된 chunksize 값을 저장할 변수
        self.init_ui()  # 사용자 인터페이스 초기화 메서드 호출

    def init_ui(self):
        """UI 레이아웃 및 위젯을 초기화하는 메서드"""
        layout = QVBoxLayout()

        # Innolink CSV 파일 선택 버튼과 라벨 추가
        layout.addWidget(QLabel("Innolink CSV 파일 선택"))
        self.inno_button = QPushButton('Browse Innolink CSV')
        self.inno_button.clicked.connect(self.load_inno_csv)
        layout.addWidget(self.inno_button)

        # Pathwise CSV 파일 선택 버튼과 라벨 추가
        layout.addWidget(QLabel("Pathwise CSV 파일 선택"))
        self.pw_button = QPushButton('Browse Pathwise CSV')
        self.pw_button.clicked.connect(self.load_pw_csv)
        layout.addWidget(self.pw_button)

        # BEL 값 입력 텍스트 에디터와 라벨 추가
        layout.addWidget(QLabel("BEL 값 입력"))
        self.bel_input = QTextEdit()
        layout.addWidget(self.bel_input)

        # BEL 비교 실행 버튼 추가
        self.compare_button = QPushButton('BEL 비교')
        self.compare_button.clicked.connect(self.compare_bel)
        layout.addWidget(self.compare_button)

        # 비교 결과를 표시할 테이블 위젯 추가
        layout.addWidget(QLabel("비교 결과"))
        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 불가 설정
        self.result_table.horizontalHeader().setSectionsClickable(True)  # 헤더 클릭 가능 설정
        self.result_table.horizontalHeader().setSortIndicatorShown(True)  # 정렬 표시기 표시 설정
        self.result_table.horizontalHeader().sectionClicked.connect(self.handle_header_click)  # 헤더 클릭 시 정렬 기능 연결
        layout.addWidget(self.result_table)

        # 콘솔 출력을 위한 텍스트 에디터 추가
        layout.addWidget(QLabel("콘솔 출력"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)  # 읽기 전용 설정
        self.console_output.setMaximumHeight(150)  # 콘솔 창의 최대 높이 설정
        layout.addWidget(self.console_output)

        # 하단에 ProgressBar와 카운트 정보를 표시할 레이아웃 추가
        bottom_layout = QHBoxLayout()

        # ProgressBar 추가
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)  # 텍스트 표시 설정
        bottom_layout.addWidget(self.progress_bar)

        # Pathwise CSV의 레코드 수를 표시할 라벨 추가
        self.pw_count_label = QLabel("Pathwise Count: 0")
        bottom_layout.addWidget(self.pw_count_label, alignment=Qt.AlignRight)

        # Innolink CSV의 레코드 수를 표시할 라벨 추가
        self.inno_count_label = QLabel("Innolink Count: 0")
        bottom_layout.addWidget(self.inno_count_label, alignment=Qt.AlignRight)

        # 에러 카운트를 표시할 라벨 추가
        self.error_count_label = QLabel("Errors: 0")
        bottom_layout.addWidget(self.error_count_label, alignment=Qt.AlignRight)

        # CSV 내보내기 버튼 추가
        self.export_button = QPushButton('CSV 내보내기')
        self.export_button.clicked.connect(self.export_csv)
        bottom_layout.addWidget(self.export_button, alignment=Qt.AlignRight)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.setWindowTitle('BEL Comparator')

        # 윈도우 초기 크기 설정
        self.resize(1200, 900)
        self.center()  # 화면 중앙에 윈도우 배치

    def center(self):
        """화면 중앙에 윈도우를 배치하는 메서드"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def log_to_console(self, message):
        """콘솔 창에 로그 메시지를 출력하는 메서드"""
        self.console_output.append(message)

    def get_system_memory_info(self):
        """시스템 메모리 정보를 MB 단위로 반환하는 메서드"""
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

    def calculate_dynamic_chunksize(self, base_chunksize=10000, cache_duration=20):
        """시스템 메모리 정보를 기반으로 동적으로 chunksize를 계산하는 메서드"""
        current_time = time.time()
        if self.cached_chunksize and (current_time - self.last_memory_check_time) < cache_duration:
            return self.cached_chunksize  # 캐시된 chunksize 값을 반환

        available_memory_mb = self.get_system_memory_info()
        target_memory_usage_mb = available_memory_mb * 0.05
        estimated_memory_per_row_mb = 0.001

        calculated_chunksize = int(target_memory_usage_mb / estimated_memory_per_row_mb)
        self.cached_chunksize = min(max(base_chunksize, calculated_chunksize), 1000000)
        self.last_memory_check_time = current_time
        return self.cached_chunksize

    def load_inno_csv(self):
        """Innolink CSV 파일을 선택하고 로드하는 메서드"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Innolink CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.inno_csv_path = file_name
            self.inno_button.setText(f"Innolink CSV: {file_name}")
            self.inno_df = self.load_csv_with_chunksize(file_name)
            self.log_to_console(f"Innolink CSV 파일 로드 완료: {file_name}")

    def load_pw_csv(self):
        """Pathwise CSV 파일을 선택하고 로드하는 메서드"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Pathwise CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.pw_csv_path = file_name
            self.pw_button.setText(f"Pathwise CSV: {file_name}")
            self.pw_df = self.load_csv_with_chunksize(file_name)
            self.log_to_console(f"Pathwise CSV 파일 로드 완료: {file_name}")

    def load_csv_with_chunksize(self, file_name):
        """동적으로 계산된 chunksize를 사용하여 CSV 파일을 로드하는 메서드"""
        chunksize = self.calculate_dynamic_chunksize()
        chunks = pd.read_csv(file_name, chunksize=chunksize)
        df = pd.concat(chunk for chunk in chunks)
        return df

    def compare_bel(self):
        """Innolink와 Pathwise 데이터를 비교하여 결과를 표시하는 메서드"""
        try:
            # Innolink CSV 파일 다시 로드
            if self.inno_csv_path:
                self.inno_df = self.load_csv_with_chunksize(self.inno_csv_path)
                self.log_to_console(f"Innolink CSV 파일 다시 로드 완료: {self.inno_csv_path}")
            else:
                self.log_to_console("Innolink CSV 파일 경로가 지정되지 않았습니다.")
                return

            # Pathwise CSV 파일 다시 로드
            if self.pw_csv_path:
                self.pw_df = self.load_csv_with_chunksize(self.pw_csv_path)
                self.log_to_console(f"Pathwise CSV 파일 다시 로드 완료: {self.pw_csv_path}")
            else:
                self.log_to_console("Pathwise CSV 파일 경로가 지정되지 않았습니다.")
                return

            # BEL 값 입력 확인
            bel_input_text = self.bel_input.toPlainText().strip()
            if not bel_input_text:
                self.log_to_console("BEL 값을 입력하세요.")
                return

            # BEL 값을 파싱
            bel_values = BELComparator.parse_bel_values(bel_input_text)

            # 데이터 프레임의 컬럼 이름을 대문자로 변환
            self.inno_df.columns = [col.upper() for col in self.inno_df.columns]
            self.pw_df.columns = [col.upper() for col in self.pw_df.columns]

            # BEL 비교 수행
            comparator = BELComparator(self.inno_df, self.pw_df, bel_values)
            comparator.validate_and_prepare_data()

            # ProgressBar 설정
            self.progress_bar.setMaximum(len(self.pw_df))
            self.progress_bar.setValue(0)

            # 비교 결과 생성
            result = comparator.compare_bel()
            self.result_df = result.copy()  # 결과를 인스턴스 변수로 저장

            # 테이블 초기화 및 결과 표시
            self.result_table.clear()
            self.result_table.setRowCount(len(result))
            self.result_table.setColumnCount(len(result.columns))
            self.result_table.setHorizontalHeaderLabels(result.columns)

            font_metrics = QFontMetrics(self.result_table.font())

            error_count = 0

            for row_idx, row in result.iterrows():
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.result_table.setItem(row_idx, col_idx, item)
                    width = font_metrics.width(str(value)) + 10
                    self.result_table.setColumnWidth(col_idx, max(self.result_table.columnWidth(col_idx), width))

                # DIFF 값이 NaN이거나 0이 아닌 경우 에러로 간주
                try:
                    if pd.isna(row['DIFF']) or float(row['DIFF']) != 0:
                        error_count += 1
                except ValueError:
                    error_count += 1

                # ProgressBar 업데이트
                self.progress_bar.setValue(row_idx + 1)

            # 결과 레이블 업데이트
            self.pw_count_label.setText(f"Pathwise Count: {len(self.pw_df)}")
            self.inno_count_label.setText(f"Innolink Count: {len(self.inno_df)}")
            self.error_count_label.setText(f"Errors: {error_count}")

            self.log_to_console("BEL 비교 완료.")
        except (MissingColumnsError, InvalidBELValuesError) as e:
            self.log_to_console(f"오류 발생: {str(e)}")
        except Exception as e:
            self.log_to_console(f"예기치 않은 오류 발생: {str(e)}")

    def export_csv(self):
        """결과 데이터를 CSV로 내보내기"""
        try:
            if hasattr(self, 'result_df') and not self.result_df.empty:
                file_name, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)")
                if file_name:
                    self.result_df.to_csv(file_name, index=False)
                    self.log_to_console(f"CSV 파일로 내보내기 완료: {file_name}")
            else:
                self.log_to_console("내보낼 데이터가 없습니다. 먼저 BEL 비교를 실행하세요.")
        except Exception as e:
            self.log_to_console(f"CSV 내보내기 오류: {str(e)}")

    def handle_header_click(self, logicalIndex):
        """헤더 클릭 시 정렬 순서를 번갈아 가며 변경"""
        self.result_table.sortItems(logicalIndex, self.sort_order)
        self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
