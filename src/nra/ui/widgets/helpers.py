"""UI 辅助函数"""

from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QWidget


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


def make_card(title: str = None) -> tuple[QFrame, QVBoxLayout]:
    """
    创建带边框的卡片容器, 返回 (frame, layout)

    可选标题在框内顶部显示
    """
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setFrameShadow(QFrame.Plain)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(8)

    if title:
        label = QLabel(title)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(label)

    return frame, layout
