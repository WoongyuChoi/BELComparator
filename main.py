import sys
import os

# 현재 디렉터리를 Python 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bel_comparator.gui import BELComparatorApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))

    comparator = BELComparatorApp()
    comparator.show()
    sys.exit(app.exec_())
