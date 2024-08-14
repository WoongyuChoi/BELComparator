from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from bel_comparator import BELComparator
from custom_exceptions import MissingColumnsError, InvalidBELValuesError

class BELComparatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.inno_csv_path = None  # Innolink CSV 파일 경로를 저장할 변수
        self.pw_csv_path = None  # Pathwise CSV 파일 경로를 저장할 변수
        self.sort_order = Qt.AscendingOrder  # 초기 정렬 순서
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Innolink CSV 파일 선택"))
        self.inno_button = QPushButton('Browse Innolink CSV')
        self.inno_button.clicked.connect(self.load_inno_csv)
        layout.addWidget(self.inno_button)

        layout.addWidget(QLabel("Pathwise CSV 파일 선택"))
        self.pw_button = QPushButton('Browse Pathwise CSV')
        self.pw_button.clicked.connect(self.load_pw_csv)
        layout.addWidget(self.pw_button)

        layout.addWidget(QLabel("BEL 값 입력"))
        self.bel_input = QTextEdit()
        layout.addWidget(self.bel_input)

        self.compare_button = QPushButton('BEL 비교')
        self.compare_button.clicked.connect(self.compare_bel)
        layout.addWidget(self.compare_button)

        layout.addWidget(QLabel("비교 결과"))
        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 불가능하게 설정
        self.result_table.horizontalHeader().setSectionsClickable(True)
        self.result_table.horizontalHeader().setSortIndicatorShown(True)
        self.result_table.horizontalHeader().sectionClicked.connect(self.handle_header_click)  # 헤더 클릭 시 정렬 기능 연결
        layout.addWidget(self.result_table)

        layout.addWidget(QLabel("콘솔 출력"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMaximumHeight(150)  # 콘솔 창의 최대 높이 설정
        layout.addWidget(self.console_output)

        self.setLayout(layout)
        self.setWindowTitle('BEL Comparator')

        # 윈도우의 초기 크기 설정
        self.resize(800, 600)
        self.center()  # 화면 중앙에 윈도우 배치

    def center(self):
        """화면 중앙에 윈도우를 배치"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def log_to_console(self, message):
        self.console_output.append(message)

    def load_inno_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Innolink CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.inno_csv_path = file_name  # 경로를 저장
            self.inno_button.setText(f"Innolink CSV: {file_name}")
            self.inno_df = BELComparator.load_csv(file_name)
            self.log_to_console(f"Innolink CSV 파일 로드 완료: {file_name}")

    def load_pw_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Pathwise CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.pw_csv_path = file_name  # 경로를 저장
            self.pw_button.setText(f"Pathwise CSV: {file_name}")
            self.pw_df = BELComparator.load_csv(file_name)
            self.log_to_console(f"Pathwise CSV 파일 로드 완료: {file_name}")

    def compare_bel(self):
        try:
            # Innolink 및 Pathwise CSV 파일을 다시 로드
            if self.inno_csv_path:
                self.inno_df = BELComparator.load_csv(self.inno_csv_path)
                self.log_to_console(f"Innolink CSV 파일 다시 로드 완료: {self.inno_csv_path}")
            else:
                self.log_to_console("Innolink CSV 파일 경로가 지정되지 않았습니다.")
                return

            if self.pw_csv_path:
                self.pw_df = BELComparator.load_csv(self.pw_csv_path)
                self.log_to_console(f"Pathwise CSV 파일 다시 로드 완료: {self.pw_csv_path}")
            else:
                self.log_to_console("Pathwise CSV 파일 경로가 지정되지 않았습니다.")
                return

            # BEL 입력값 확인
            bel_input_text = self.bel_input.toPlainText().strip()
            if not bel_input_text:
                self.log_to_console("BEL 값을 입력하세요.")
                return

            bel_values = BELComparator.parse_bel_values(bel_input_text)

            self.inno_df.columns = [col.upper() for col in self.inno_df.columns]
            self.pw_df.columns = [col.upper() for col in self.pw_df.columns]

            comparator = BELComparator(self.inno_df, self.pw_df, bel_values)
            comparator.validate_and_prepare_data()
            result = comparator.compare_bel()

            # 테이블 초기화 및 결과 표시
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

            self.log_to_console("BEL 비교 완료.")
        except (MissingColumnsError, InvalidBELValuesError) as e:
            self.log_to_console(f"오류 발생: {str(e)}")
        except Exception as e:
            self.log_to_console(f"예기치 않은 오류 발생: {str(e)}")

    def handle_header_click(self, logicalIndex):
        """헤더 클릭 시 정렬 순서를 번갈아 가며 변경"""
        self.result_table.sortItems(logicalIndex, self.sort_order)
        self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
