"""主题"""

from qfluentwidgets import setTheme, setThemeColor, Theme
from PySide6.QtGui import QColor


def apply_theme():
    # 跟随系统主题 (macOS 暗色 → 暗色, Windows 亮色 → 亮色)
    setTheme(Theme.AUTO)
    # 蓝色强调色
    setThemeColor(QColor(0, 120, 212))
