"""主题配色"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QStyleFactory


def apply_theme(app: QApplication):
    """应用统一主题: 白底深字, 蓝色强调"""
    app.setStyle(QStyleFactory.create("Fusion"))

    p = QPalette()

    # 背景
    p.setColor(QPalette.Window, QColor(250, 250, 250))
    p.setColor(QPalette.Base, QColor(255, 255, 255))
    p.setColor(QPalette.AlternateBase, QColor(245, 247, 250))

    # 文字
    p.setColor(QPalette.WindowText, QColor(30, 30, 30))
    p.setColor(QPalette.Text, QColor(30, 30, 30))
    p.setColor(QPalette.ButtonText, QColor(30, 30, 30))
    p.setColor(QPalette.BrightText, QColor(0, 0, 0))

    # 按钮
    p.setColor(QPalette.Button, QColor(238, 240, 244))

    # 强调色 (选中/高亮)
    p.setColor(QPalette.Highlight, QColor(24, 115, 204))
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.Link, QColor(24, 115, 204))

    # 提示
    p.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    p.setColor(QPalette.ToolTipText, QColor(30, 30, 30))

    # 边框/分隔线 (通过 Mid 和 Midlight 控制)
    p.setColor(QPalette.Mid, QColor(200, 204, 210))
    p.setColor(QPalette.Midlight, QColor(228, 230, 235))
    p.setColor(QPalette.Shadow, QColor(180, 184, 190))
    p.setColor(QPalette.Light, QColor(255, 255, 255))
    p.setColor(QPalette.Dark, QColor(160, 164, 170))

    # 禁用态
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(160, 164, 170))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(160, 164, 170))
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(160, 164, 170))
    p.setColor(QPalette.Disabled, QPalette.Base, QColor(245, 245, 245))

    # PlaceholderText
    p.setColor(QPalette.PlaceholderText, QColor(160, 164, 170))

    app.setPalette(p)
