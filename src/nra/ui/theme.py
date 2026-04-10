"""主题 — 使用 Fluent Design"""

from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme


def apply_theme(app: QApplication):
    setTheme(Theme.LIGHT)
