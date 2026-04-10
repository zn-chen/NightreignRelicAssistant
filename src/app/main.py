"""应用程序主入口。"""

from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))

    # 统一替换常见的系统默认字体，避免不同控件出现字体不一致。
    QFont.insertSubstitution("MS Sans Serif", "Segoe UI")
    QFont.insertSubstitution("MS Shell Dlg", "Segoe UI")
    QFont.insertSubstitution("MS Shell Dlg 2", "Segoe UI")
    QFont.insertSubstitution("System", "Segoe UI")
    QFont.insertSubstitution("Default", "Segoe UI")

    # 全局样式里补充中文字体回退，保证中文界面显示稳定。
    app.setStyleSheet(
        """
        * {
            font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            font-size: 9pt;
        }
        """
    )

    # 启动依赖容器并构建主窗口。
    container = bootstrap()
    window = MainWindow(container)
    window.show()

    # 首次启动时按窗口逻辑决定是否展示欢迎提示。
    window.maybe_show_welcome()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
