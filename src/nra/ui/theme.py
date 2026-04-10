"""主题配色 — 淡米色复古风"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QStyleFactory


def apply_theme(app: QApplication):
    """淡米色底, 深棕文字, 复古暖色调"""
    app.setStyle(QStyleFactory.create("Fusion"))

    p = QPalette()

    # 背景 — 偏暖的淡米色
    p.setColor(QPalette.Window, QColor(248, 244, 237))
    p.setColor(QPalette.Base, QColor(253, 250, 244))
    p.setColor(QPalette.AlternateBase, QColor(244, 240, 232))

    # 文字 — 深棕, 不刺眼
    p.setColor(QPalette.WindowText, QColor(50, 42, 35))
    p.setColor(QPalette.Text, QColor(50, 42, 35))
    p.setColor(QPalette.ButtonText, QColor(50, 42, 35))
    p.setColor(QPalette.BrightText, QColor(30, 25, 20))

    # 按钮 — 略深的米色
    p.setColor(QPalette.Button, QColor(235, 230, 220))

    # 强调色 — 暖棕蓝, 复古感
    p.setColor(QPalette.Highlight, QColor(140, 115, 85))
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 250))
    p.setColor(QPalette.Link, QColor(120, 90, 60))

    # 提示
    p.setColor(QPalette.ToolTipBase, QColor(253, 250, 244))
    p.setColor(QPalette.ToolTipText, QColor(50, 42, 35))

    # 边框/分隔线
    p.setColor(QPalette.Mid, QColor(200, 192, 180))
    p.setColor(QPalette.Midlight, QColor(225, 220, 210))
    p.setColor(QPalette.Shadow, QColor(170, 162, 150))
    p.setColor(QPalette.Light, QColor(253, 250, 244))
    p.setColor(QPalette.Dark, QColor(150, 142, 130))

    # 禁用态
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(170, 162, 150))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(170, 162, 150))
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(170, 162, 150))
    p.setColor(QPalette.Disabled, QPalette.Base, QColor(242, 238, 230))

    # PlaceholderText
    p.setColor(QPalette.PlaceholderText, QColor(170, 162, 150))

    app.setPalette(p)
