"""UI 辅助函数"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame, QWidget


def make_title(text: str) -> QLabel:
    """创建页面/面板标题 (15px 加粗)"""
    label = QLabel(text)
    label.setStyleSheet("font-size: 15px; font-weight: bold;")
    return label


def make_card(title: str = None) -> tuple:
    """创建带边框的卡片容器, 返回 (frame, layout)"""
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setFrameShadow(QFrame.Plain)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)

    if title:
        label = QLabel(title)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(label)

    return frame, layout
