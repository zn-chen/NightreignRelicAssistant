"""程序入口"""

import sys
import os


def main():
    from PySide6.QtWidgets import QApplication
    from nra.ui.main_window import MainWindow

    # 强制浅色模式，不被 macOS 暗色主题影响
    os.environ["QT_QPA_PLATFORM_THEME"] = ""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from nra.ui.theme import apply_theme
    apply_theme()

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    data_dir = os.path.normpath(data_dir)

    window = MainWindow(data_dir=data_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
