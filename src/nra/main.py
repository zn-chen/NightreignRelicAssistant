"""程序入口"""

import sys
import os


def main():
    from PySide6.QtWidgets import QApplication
    from nra.ui.main_window import MainWindow

    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QGroupBox {
            font-size: 14px;
            font-weight: bold;
            margin-top: 8px;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
        }
    """)

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    data_dir = os.path.normpath(data_dir)

    window = MainWindow(data_dir=data_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
