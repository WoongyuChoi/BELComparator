from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QTableWidget,
    QProgressBar, QHBoxLayout, QAbstractItemView, QLineEdit, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

def init_ui(app_instance):
    """UI를 초기화하는 함수"""
    layout = QVBoxLayout()

    layout.addWidget(QLabel("Innolink CSV 파일 선택"))
    app_instance.inno_button = QPushButton('Browse Innolink CSV')
    app_instance.inno_button.clicked.connect(app_instance.load_inno_csv)
    layout.addWidget(app_instance.inno_button)

    layout.addWidget(QLabel("Pathwise CSV 파일 선택"))
    app_instance.pw_button = QPushButton('Browse Pathwise CSV')
    app_instance.pw_button.clicked.connect(app_instance.load_pw_csv)
    layout.addWidget(app_instance.pw_button)

    # BEL 값 입력란
    layout.addWidget(QLabel("BEL 값 입력"))
    app_instance.bel_input = QTextEdit()
    layout.addWidget(app_instance.bel_input)

    # 데이터 범위 설정 입력란
    range_layout_container = QHBoxLayout()  # 전체 레이아웃을 감싸는 컨테이너
    empty_space_layout = QHBoxLayout()  # 빈 공간을 채우기 위한 레이아웃
    range_layout = QHBoxLayout()  # 실제로 데이터를 입력받는 레이아웃
    
    range_layout.addWidget(QLabel("데이터 범위 설정"))
    app_instance.start_input = QLineEdit()
    app_instance.start_input.setPlaceholderText("시작 (기본값: 0)")
    range_layout.addWidget(app_instance.start_input)

    range_layout.addWidget(QLabel(" ~ "))  # 물결 기호

    app_instance.end_input = QLineEdit()
    app_instance.end_input.setPlaceholderText("종료 (기본값: 최대값)")
    range_layout.addWidget(app_instance.end_input)

    # SpacerItem을 사용하여 빈 공간을 채움
    spacer = QSpacerItem(300, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
    range_layout_container.addLayout(range_layout, stretch=1)
    range_layout_container.addSpacerItem(spacer)

    layout.addLayout(range_layout_container)

    # 허용오차 입력란과 BEL 비교 버튼을 같은 행에 배치
    adjustment_layout = QHBoxLayout()
    
    adjustment_layout.addWidget(QLabel("허용오차 입력 (기본값: 0.001)"))
    app_instance.adjustment_input = QLineEdit()
    app_instance.adjustment_input.setPlaceholderText("0.001")
    adjustment_layout.addWidget(app_instance.adjustment_input, 1)  # 비율 1

    app_instance.compare_button = QPushButton('BEL 비교')
    app_instance.compare_button.clicked.connect(app_instance.compare_bel)
    adjustment_layout.addWidget(app_instance.compare_button, 1)  # 비율 1

    layout.addLayout(adjustment_layout)

    layout.addWidget(QLabel("비교 결과"))
    app_instance.result_table = QTableWidget()
    app_instance.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    app_instance.result_table.horizontalHeader().setSectionsClickable(True)
    app_instance.result_table.horizontalHeader().setSortIndicatorShown(True)
    app_instance.result_table.horizontalHeader().sectionClicked.connect(app_instance.handle_header_click)
    layout.addWidget(app_instance.result_table)

    layout.addWidget(QLabel("콘솔 출력"))
    app_instance.console_output = QTextEdit()
    app_instance.console_output.setReadOnly(True)
    app_instance.console_output.setMaximumHeight(150)
    layout.addWidget(app_instance.console_output)

    bottom_layout = QHBoxLayout()
    app_instance.progress_bar = QProgressBar()
    app_instance.progress_bar.setTextVisible(True)
    bottom_layout.addWidget(app_instance.progress_bar)

    app_instance.pw_count_label = QLabel("Pathwise Count: 0")
    bottom_layout.addWidget(app_instance.pw_count_label, alignment=Qt.AlignRight)

    app_instance.inno_count_label = QLabel("Innolink Count: 0")
    bottom_layout.addWidget(app_instance.inno_count_label, alignment=Qt.AlignRight)

    app_instance.error_count_label = QLabel("Errors: 0")
    bottom_layout.addWidget(app_instance.error_count_label, alignment=Qt.AlignRight)

    app_instance.export_button = QPushButton('CSV 내보내기')
    app_instance.export_button.clicked.connect(app_instance.export_csv)
    bottom_layout.addWidget(app_instance.export_button, alignment=Qt.AlignRight)

    layout.addLayout(bottom_layout)
    app_instance.setLayout(layout)
    app_instance.setWindowTitle('BEL Comparator')

    # 화면 해상도에 따른 윈도우 크기 조정
    adjust_window_size(app_instance)
    center(app_instance)

def adjust_window_size(app_instance):
    """해상도에 따라 윈도우 크기를 조정하는 함수"""
    screen_geometry = app_instance.screen().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    # 기본 비율 설정 (화면 크기의 50%)
    width_ratio = 0.5
    height_ratio = 0.5

    # 전체 화면 크기의 비율로 윈도우 크기 설정
    window_width = int(screen_width * width_ratio)
    window_height = int(screen_height * height_ratio)

    # 최소 크기 설정
    min_width = 800
    min_height = 600

    # 최소 크기보다 작은 경우, 최소 크기로 설정
    window_width = max(window_width, min_width)
    window_height = max(window_height, min_height)

    app_instance.resize(window_width, window_height)

def center(app_instance):
    """화면 중앙에 윈도우를 배치하는 함수"""
    qr = app_instance.frameGeometry()
    cp = app_instance.screen().availableGeometry().center()
    qr.moveCenter(cp)
    app_instance.move(qr.topLeft())

def log_to_console(app_instance, message):
    """콘솔 창에 로그 메시지를 출력하는 함수"""
    app_instance.console_output.append(message)
