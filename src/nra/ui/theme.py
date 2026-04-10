"""主题 — 强制浅色，不跟随系统"""

from qfluentwidgets import setTheme, setThemeColor, Theme
from PySide6.QtGui import QColor


def apply_theme():
    # 强制浅色主题，不受 macOS 暗色模式影响
    setTheme(Theme.LIGHT)
    # 主题强调色
    setThemeColor(QColor(0, 120, 212))
