"""首次启动欢迎对话框。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QVBoxLayout
from qfluentwidgets import CardWidget, PrimaryPushButton


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用须知")
        self.setFixedWidth(520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._never_show_again = QCheckBox("不再提示")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("使用须知")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22pt; font-weight: bold;")
        layout.addWidget(title)

        notices = [
            (
                "1. 游戏亮度设置",
                "请将游戏『显示设置』中的亮度调为 6，否则仓库清理功能中遗物状态检测可能会出错。",
            ),
            (
                "2. 分辨率要求",
                "本程序支持多分辨率及各种显示模式，但分辨率过低时遗物词条的 OCR 识别准确率会下降。",
            ),
            (
                "3. 非 16:9 屏幕",
                "若显示器并非 16:9，请尽量使用窗口化或拉伸全屏，避免坐标缩放偏移。",
            ),
        ]

        for title_text, body_text in notices:
            card = CardWidget(self)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 10, 14, 10)
            card_layout.setSpacing(4)

            heading = QLabel(title_text)
            heading.setFont(QFont("Segoe UI", 10, QFont.Bold))
            heading.setStyleSheet("font-size: 10pt; font-weight: bold;")
            card_layout.addWidget(heading)

            body = QLabel(body_text)
            body.setFont(QFont("Segoe UI", 9))
            body.setWordWrap(True)
            body.setStyleSheet("color: #555;")
            card_layout.addWidget(body)

            layout.addWidget(card)

        bottom = QHBoxLayout()
        bottom.addWidget(self._never_show_again)
        bottom.addStretch(1)

        ok_button = PrimaryPushButton("我知道了")
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        bottom.addWidget(ok_button)
        layout.addLayout(bottom)

    def should_hide_forever(self) -> bool:
        return self._never_show_again.isChecked()
