"""UI 辅助函数"""

from PySide6.QtWidgets import QLabel


def make_title(text: str) -> QLabel:
    """创建页面/面板标题"""
    label = QLabel(text)
    label.setStyleSheet("font-size: 15px; font-weight: bold;")
    return label


def make_section(text: str) -> QLabel:
    """创建小节标题"""
    label = QLabel(text)
    label.setStyleSheet("font-size: 13px; font-weight: bold; color: gray;")
    return label
