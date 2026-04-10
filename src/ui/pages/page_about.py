"""关于页。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget


class AboutPage(QWidget):
    developer_mode_activated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AboutPage")
        self.click_count = 0
        self._developer_mode = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._reset_counter)
        self._init_ui()

    def _init_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        outer_layout.addWidget(scroll_area)

        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("关于", content)
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)

        info_card = CardWidget(content)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(8)

        app_name = QLabel("Nightreign Relic Assistant", info_card)
        app_name.setStyleSheet("font-size: 18pt; font-weight: bold;")
        info_layout.addWidget(app_name)

        desc_text = QLabel("艾尔登法环：黑夜君临 遗物辅助管理工具", info_card)
        desc_text.setFont(QFont("Segoe UI", 10))
        desc_text.setStyleSheet("color: #555;")
        info_layout.addWidget(desc_text)
        layout.addWidget(info_card)

        version_card = CardWidget(content)
        version_card.setCursor(Qt.PointingHandCursor)
        version_layout = QVBoxLayout(version_card)
        version_layout.setContentsMargins(24, 20, 24, 20)
        version_layout.setSpacing(8)

        version_title = QLabel("版本", version_card)
        version_title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        version_layout.addWidget(version_title)

        self.version_label = QLabel("v0.1.0", version_card)
        self.version_label.setFont(QFont("Segoe UI", 9))
        self.version_label.setStyleSheet("color: gray;")
        version_layout.addWidget(self.version_label)
        version_card.mousePressEvent = self._on_version_clicked
        layout.addWidget(version_card)

        reference_card = CardWidget(content)
        reference_layout = QVBoxLayout(reference_card)
        reference_layout.setContentsMargins(24, 20, 24, 20)
        reference_layout.setSpacing(8)

        reference_title = QLabel("项目说明", reference_card)
        reference_title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        reference_layout.addWidget(reference_title)

        reference_desc = QLabel(
            "本项目保留参考工具的交互形态和产品结构，但将OCR、规则和业务编排边界做了拆分，"
            "便于替换为你自己的识别与判定逻辑。",
            reference_card,
        )
        reference_desc.setWordWrap(True)
        reference_desc.setFont(QFont("Segoe UI", 9))
        reference_desc.setStyleSheet("color: gray;")
        reference_layout.addWidget(reference_desc)
        layout.addWidget(reference_card)

        disclaimer_card = CardWidget(content)
        disclaimer_layout = QVBoxLayout(disclaimer_card)
        disclaimer_layout.setContentsMargins(24, 20, 24, 20)
        disclaimer_layout.setSpacing(8)

        disclaimer_title = QLabel("免责声明", disclaimer_card)
        disclaimer_title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        disclaimer_layout.addWidget(disclaimer_title)

        disclaimer_text = QLabel(
            "本软件仅供学习交流使用，使用本软件产生的风险由使用者自行承担。\n\n"
            "• 本软件通过OCR识别与自动化辅助操作，不修改游戏文件\n"
            "• 使用前请自行确认是否符合你的使用边界和风险承受范围\n"
            "• 开发者不对账号处罚、数据丢失或其他连带问题负责",
            disclaimer_card,
        )
        disclaimer_text.setFont(QFont("Segoe UI", 9))
        disclaimer_text.setWordWrap(True)
        disclaimer_text.setStyleSheet("color: #666;")
        disclaimer_layout.addWidget(disclaimer_text)
        layout.addWidget(disclaimer_card)

        layout.addStretch(1)
        scroll_area.setWidget(content)

    def _on_version_clicked(self, event) -> None:
        _ = event
        if self._developer_mode:
            return

        # 版本号区域保留一个隐藏入口，连续点击后才显示开发者设置。
        self.click_count += 1
        self._timer.start()
        if self.click_count >= 5:
            self._developer_mode = True
            self.click_count = 0
            self._timer.stop()
            self.developer_mode_activated.emit()

    def _reset_counter(self) -> None:
        self.click_count = 0
