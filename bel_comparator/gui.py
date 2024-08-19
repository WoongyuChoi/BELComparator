import pandas as pd
from PyQt5.QtWidgets import QWidget, QFileDialog, QAbstractItemView, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
import bel_comparator.ui_setup as ui_setup  # UI 설정 모듈
import bel_comparator.utils as utils  # 유틸리티 함수 모듈
import bel_comparator.data_processing as data_processing  # 데이터 처리 모듈
from bel_comparator import BELComparator  # BELComparator 클래스 임포트

class BELComparatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.inno_csv_path = None
        self.pw_csv_path = None
        self.sort_order = Qt.AscendingOrder
        self.last_memory_check_time = 0
        self.cached_chunksize = None
        ui_setup.init_ui(self)

    def center(self):
        ui_setup.center(self)

    def log_to_console(self, message):
        ui_setup.log_to_console(self, message)

    def load_inno_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Innolink CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.inno_csv_path = file_name
            self.inno_button.setText(f"Innolink CSV: {file_name}")
            self.cached_chunksize, self.last_memory_check_time = utils.calculate_dynamic_chunksize(
                self.last_memory_check_time, self.cached_chunksize)
            self.inno_df = utils.load_csv_with_chunksize(file_name, self.cached_chunksize)
            self.log_to_console(f"Innolink CSV 파일 로드 완료: {file_name}")

    def load_pw_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Pathwise CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.pw_csv_path = file_name
            self.pw_button.setText(f"Pathwise CSV: {file_name}")
            self.cached_chunksize, self.last_memory_check_time = utils.calculate_dynamic_chunksize(
                self.last_memory_check_time, self.cached_chunksize)
            self.pw_df = utils.load_csv_with_chunksize(file_name, self.cached_chunksize)
            self.log_to_console(f"Pathwise CSV 파일 로드 완료: {file_name}")

    def compare_bel(self):
        try:
            if self.inno_csv_path:
                self.inno_df = utils.load_csv_with_chunksize(self.inno_csv_path, self.cached_chunksize)
                self.log_to_console(f"Innolink CSV 파일 다시 로드 완료: {self.inno_csv_path}")
            else:
                self.log_to_console("Innolink CSV 파일 경로가 지정되지 않았습니다.")
                return

            if self.pw_csv_path:
                self.pw_df = utils.load_csv_with_chunksize(self.pw_csv_path, self.cached_chunksize)
                self.log_to_console(f"Pathwise CSV 파일 다시 로드 완료: {self.pw_csv_path}")
            else:
                self.log_to_console("Pathwise CSV 파일 경로가 지정되지 않았습니다.")
                return

            bel_input_text = self.bel_input.toPlainText().strip()
            if not bel_input_text:
                self.log_to_console("BEL 값을 입력하세요.")
                return
            
            # 데이터 범위 입력 값 검증 및 설정
            start_str = self.start_input.text().strip()
            end_str = self.end_input.text().strip()

            # 기본값 설정
            start = 0
            end = len(self.inno_df)

            # start 값 검증 및 설정
            if start_str:
                if start_str.isdigit():
                    start = int(start_str)
                    if start < 0:
                        self.log_to_console("시작 값은 0 이상이어야 합니다.")
                        return
                else:
                    self.log_to_console("시작 값은 정수여야 합니다.")
                    return

            # end 값 검증 및 설정
            if end_str:
                if end_str.isdigit():
                    end = int(end_str)
                    if end > len(self.inno_df):
                        end = len(self.inno_df)  # 최대 값으로 설정
                    if end < start:
                        self.log_to_console("종료 값은 시작 값보다 크거나 같아야 합니다.")
                        return
                else:
                    self.log_to_console("종료 값은 정수여야 합니다.")
                    return

            # 데이터 프레임 자르기
            self.inno_df = self.inno_df.iloc[start:end + 1]
            bel_values = BELComparator.parse_bel_values(bel_input_text)
            self.inno_df.columns = [col.upper() for col in self.inno_df.columns]
            self.pw_df.columns = [col.upper() for col in self.pw_df.columns]

            # 조정계수 값 읽기 및 유효성 검사
            adjustment_factor_str = self.adjustment_input.text().strip()
            adjustment_factor = 0.001
            if adjustment_factor_str:
                adjustment_factor = float(adjustment_factor_str)            
                if adjustment_factor < 0.000001 or adjustment_factor > 1:
                    self.log_to_console("조정계수는 0.000001 이상 1 이하의 값이어야 합니다.")
                    return

            result, error_count = data_processing.compare_bel(
                self.inno_df, self.pw_df, bel_values, self.progress_bar, self.log_to_console, adjustment_factor
            )

            if result is not None:
                self.result_df = result.copy()
                self.result_table.clear()
                self.result_table.setRowCount(len(result))
                self.result_table.setColumnCount(len(result.columns))
                self.result_table.setHorizontalHeaderLabels(result.columns)

                font_metrics = QFontMetrics(self.result_table.font())
                for row_idx, row in result.iterrows():
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.result_table.setItem(row_idx, col_idx, item)
                        width = font_metrics.width(str(value)) + 10
                        self.result_table.setColumnWidth(col_idx, max(self.result_table.columnWidth(col_idx), width))

                self.pw_count_label.setText(f"Pathwise Count: {len(self.pw_df)}")
                self.inno_count_label.setText(f"Innolink Count: {len(self.inno_df)}")
                self.error_count_label.setText(f"Errors: {error_count}")

                self.log_to_console("BEL 비교 완료.")
        except Exception as e:
            self.log_to_console(f"예기치 않은 오류 발생: {str(e)}")

    def export_csv(self):
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
        self.result_table.sortItems(logicalIndex, self.sort_order)
        self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
