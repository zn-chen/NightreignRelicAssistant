"""首页 — 占位页面"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class HomePage(QWidget):
    """简单的欢迎/占位首页。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("黑夜君临遗物助手")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #cdd6f4;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("v0.1.0")
        version.setStyleSheet("font-size: 14pt; color: #585b70;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        desc = QLabel("Elden Ring Nightreign 遗物自动化管理工具")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
