"""卡片容器"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


def make_card(title=None):
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)
    if title:
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
    return frame, layout
