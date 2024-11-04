import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

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
        self.original_result_df = None  # 원본 결과 저장용
        self.filtered_result_df = None  # 필터링된 결과 저장용
        self.adjustment_factor = 0.001
        ui_setup.init_ui(self)

        # 라디오 버튼 및 체크박스 클릭 시 필터링 함수 연결
        self.all_radio.clicked.connect(self.apply_filter)
        self.diff_radio.clicked.connect(self.apply_filter)
        self.na_checkbox.clicked.connect(self.apply_filter)

    def center(self):
        ui_setup.center(self)

    def log_to_console(self, message):
        ui_setup.log_to_console(self, message)

    def load_inno_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select First CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.inno_csv_path = file_name
            self.inno_button.setText(f"First CSV: {file_name}")
            self.cached_chunksize, self.last_memory_check_time = utils.calculate_dynamic_chunksize(
                self.last_memory_check_time, self.cached_chunksize)

    def load_pw_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Second CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.pw_csv_path = file_name
            self.pw_button.setText(f"Second CSV: {file_name}")
            self.cached_chunksize, self.last_memory_check_time = utils.calculate_dynamic_chunksize(
                self.last_memory_check_time, self.cached_chunksize)

    def apply_filter(self):
        """라디오 버튼 및 체크박스 상태에 따라 결과를 필터링하여 표시"""
        if self.original_result_df is None:
            self.log_to_console("BEL 비교를 먼저 실행하세요.")
            return
        
        # 초기화
        self.filtered_result_df = self.original_result_df.copy()              
        
        # 필터링 작업 (전체조회, 오차조회, N/A 제외)
        if self.diff_radio.isChecked():
            self.log_to_console("오차조회 선택됨.")
            self.filtered_result_df = self.filtered_result_df[self.filtered_result_df['DIFF'].apply(
                lambda x: x == 'NaN' or (utils.is_valid_float(x) and abs(float(x)) >= self.adjustment_factor)
            )]
        else:
            self.log_to_console("전체조회 선택됨.")

        if self.na_checkbox.isChecked():
            self.log_to_console("N/A 제외 선택됨.")
            self.filtered_result_df = self.filtered_result_df[self.filtered_result_df['DIFF'] != 'NaN']
        
        # 배열 Index 재설정
        self.filtered_result_df = self.filtered_result_df.fillna('NaN')
        self.filtered_result_df = self.filtered_result_df.infer_objects(copy=False)
        self.filtered_result_df = self.filtered_result_df.reset_index(drop=True)

        # 에러 카운트를 계산
        error_count = data_processing.calculate_error_count(
            self.filtered_result_df,
            self.adjustment_factor,
            self.na_checkbox.isChecked()
        )

        # 에러 카운트를 업데이트
        self.error_count_label.setText(f"Errors: {error_count}")

        # 필터링된 결과를 테이블에 표시
        self.update_result_table(self.filtered_result_df)

    def update_result_table(self, result):
        """결과를 테이블에 업데이트하는 함수"""
        self.result_table.clear()
        self.result_table.setRowCount(len(result))
        self.result_table.setColumnCount(len(result.columns))
        self.result_table.setHorizontalHeaderLabels(result.columns)

        font_metrics = QFontMetrics(self.result_table.font())

        for row_idx, row in result.iterrows():
            for col_idx, value in enumerate(row):
                if value == '' or pd.isna(value):
                    value = 'NaN'
                item = QTableWidgetItem(str(value))
                self.result_table.setItem(row_idx, col_idx, item)
                width = font_metrics.width(str(value)) + 10
                self.result_table.setColumnWidth(col_idx, max(self.result_table.columnWidth(col_idx), width))

    def compare_bel(self):
        try:
            # BEL 비교를 시작할 때 콘솔 창 클리어
            self.console_output.clear()
            
            if self.inno_csv_path:
                self.inno_df = utils.load_csv_with_chunksize(self.inno_csv_path, self.cached_chunksize)
                self.log_to_console(f"Innolink CSV 파일 로드 완료: {self.inno_csv_path}")
            else:
                self.log_to_console("Innolink CSV 파일 경로가 지정되지 않았습니다.")
                return

            if self.pw_csv_path:
                self.pw_df = utils.load_csv_with_chunksize(self.pw_csv_path, self.cached_chunksize)
                self.log_to_console(f"Pathwise CSV 파일 로드 완료: {self.pw_csv_path}")
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

            # 허용오차 값 읽기 및 유효성 검사
            adjustment_factor_str = self.adjustment_input.text().strip()
            if adjustment_factor_str:
                self.adjustment_factor = float(adjustment_factor_str)            
                if self.adjustment_factor < 0.000001 or self.adjustment_factor > 1:
                    self.log_to_console("허용오차는 0.000001 이상 1 이하의 값이어야 합니다.")
                    return

            result = data_processing.compare_bel(
                self.inno_df,
                self.pw_df,
                bel_values,
                self.progress_bar,
                self.log_to_console
            )

            if result is not None:
                self.original_result_df = result.copy()
                self.apply_filter()  # 필터를 바로 적용하여 화면에 표시

                self.pw_count_label.setText(f"Pathwise Count: {len(self.pw_df)}")
                self.inno_count_label.setText(f"Innolink Count: {len(self.inno_df)}")

                self.log_to_console("BEL 비교 완료.")
        except Exception as e:
            self.log_to_console(f"예기치 않은 오류 발생: {str(e)}")

    def export_csv(self):
        try:
            if hasattr(self, 'filtered_result_df') and not self.filtered_result_df.empty:
                file_name, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)")
                if file_name:
                    self.filtered_result_df.to_csv(file_name, index=False)
                    self.log_to_console(f"CSV 파일로 내보내기 완료: {file_name}")
            else:
                self.log_to_console("내보낼 데이터가 없습니다. 먼저 BEL 비교를 실행하세요.")
        except Exception as e:
            self.log_to_console(f"CSV 내보내기 오류: {str(e)}")

    def handle_header_click(self, logicalIndex):
        self.result_table.sortItems(logicalIndex, self.sort_order)
        self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
