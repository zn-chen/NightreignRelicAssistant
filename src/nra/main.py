"""程序入口"""

import sys


def main():
    from PySide6.QtWidgets import QApplication
    from nra.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
