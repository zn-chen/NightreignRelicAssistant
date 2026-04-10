"""商店筛选页。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QTabWidget, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, PrimaryPushButton, PushButton

from core.models.runtime import AppSettings
from services.history_service import HistoryService
from services.shop_service import ShopService
from ui.components import LoggerWidget, StableComboBox, StatsPanel
from ui.workers.shop_worker import ShopWorker


class ShopPage(QWidget):
    def __init__(self, history_service: HistoryService, shop_service: ShopService, parent=None):
        super().__init__(parent)
        self.setObjectName("ShopPage")
        self.history_service = history_service
        self.shop_service = shop_service
        self.settings = AppSettings()
        self.worker: ShopWorker | None = None
        self._ocr_ready = False

        self.logger = LoggerWidget(self)
        self.stats_panel = StatsPanel(["已购买", "合格", "不合格", "已售出"])

        self._qualified_container = QWidget(self)
        self._qualified_layout = QVBoxLayout(self._qualified_container)
        self._qualified_layout.setContentsMargins(0, 0, 0, 0)
        self._qualified_layout.setSpacing(6)

        self._init_ui()
        self._refresh_history()
        self._reset_stats()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(6)

        title = QLabel("商店筛选")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(self._create_toolbar())
        layout.addWidget(self._create_right_panel(), 1)

    def _create_toolbar(self) -> CardWidget:
        card = CardWidget(self)
        card.setFixedHeight(60)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        layout.addWidget(QLabel("模式:"))
        self.mode_combo = StableComboBox(card)
        self.mode_combo.addItems(["普通", "深夜"])
        self.mode_combo.setFixedWidth(100)
        layout.addWidget(self.mode_combo)

        layout.addSpacing(10)
        layout.addWidget(QLabel("版本:"))
        self.version_combo = StableComboBox(card)
        self.version_combo.addItems(["新版", "旧版"])
        self.version_combo.setFixedWidth(100)
        layout.addWidget(self.version_combo)

        layout.addSpacing(10)
        self.currency_label = QLabel("停止暗痕:")
        layout.addWidget(self.currency_label)

        self.currency_input = QLineEdit(card)
        self.currency_input.setText("5000")
        self.currency_input.setFixedWidth(120)
        self.currency_input.setFixedHeight(33)
        self.currency_input.setValidator(QIntValidator(0, 2147483647, self))
        self.currency_input.setPlaceholderText("输入暗痕数量")
        layout.addWidget(self.currency_input)

        self.target_label = QLabel("停止合格遗物数量:")
        self.target_label.setVisible(False)
        layout.addWidget(self.target_label)

        self.target_input = QLineEdit(card)
        self.target_input.setText("1")
        self.target_input.setFixedWidth(120)
        self.target_input.setFixedHeight(33)
        self.target_input.setValidator(QIntValidator(1, 999, self))
        self.target_input.setPlaceholderText("合格遗物数")
        self.target_input.setVisible(False)
        layout.addWidget(self.target_input)

        layout.addStretch(1)

        self.start_button = PrimaryPushButton("初始化OCR...", card)
        self.start_button.setFixedHeight(36)
        self.start_button.setFixedWidth(120)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._on_start)
        layout.addWidget(self.start_button)

        self.stop_button = PushButton("停止", card)
        self.stop_button.setFixedHeight(36)
        self.stop_button.setFixedWidth(80)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop)
        layout.addWidget(self.stop_button)

        return card

    def _create_right_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        tabs = QTabWidget(panel)
        tabs.addTab(self.logger, "日志")
        tabs.addTab(self._create_dashboard(), "仪表盘")
        layout.addWidget(tabs)
        return panel

    def _create_dashboard(self) -> QWidget:
        dashboard = QWidget(self)
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self.stats_panel)

        group = QGroupBox("合格遗物词条", dashboard)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(4)

        clear_button = PushButton("清空记录", group)
        clear_button.clicked.connect(self._clear_history)
        group_layout.addWidget(clear_button)

        scroll = QScrollArea(group)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._qualified_container)
        group_layout.addWidget(scroll)

        layout.addWidget(group, 1)
        return dashboard

    def set_ocr_ready(self, ready: bool) -> None:
        self._ocr_ready = ready
        self.start_button.setEnabled(ready)
        self.start_button.setText("开始购买" if ready else "初始化OCR...")

    def update_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        sl_enabled = settings.sl_mode_enabled
        self.currency_label.setVisible(not sl_enabled)
        self.currency_input.setVisible(not sl_enabled)
        self.target_label.setVisible(sl_enabled)
        self.target_input.setVisible(sl_enabled)

    def _reset_stats(self) -> None:
        self.stats_panel.set_values({"已购买": 0, "合格": 0, "不合格": 0, "已售出": 0})

    def _refresh_history(self) -> None:
        # 商店页只展示“合格遗物”历史，因此刷新时固定读取单一记录桶。
        while self._qualified_layout.count():
            item = self._qualified_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        records = list(reversed(self.history_service.list_records("shop_qualified")))
        if not records:
            placeholder = QLabel("暂无合格遗物记录", self._qualified_container)
            placeholder.setStyleSheet("color: gray; padding: 12px 0;")
            placeholder.setAlignment(Qt.AlignCenter)
            self._qualified_layout.addWidget(placeholder)
            return

        for record in records[:30]:
            self._qualified_layout.addWidget(self._build_record_card(record))
        self._qualified_layout.addStretch(1)

    def _build_record_card(self, record: dict) -> QWidget:
        card = CardWidget(self._qualified_container)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        heading = QLabel(f"第 {record.get('index', 0)} 件  ·  {record.get('created_at', '')}", card)
        heading.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(heading)

        affix_text = " / ".join(item.get("text", "") for item in record.get("affixes", [])) or "无词条数据"
        affix_label = QLabel(affix_text, card)
        affix_label.setWordWrap(True)
        affix_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        layout.addWidget(affix_label)

        reason = record.get("extra", {}).get("reason")
        if reason:
            reason_label = QLabel(str(reason), card)
            reason_label.setWordWrap(True)
            reason_label.setStyleSheet("color: #777; font-size: 9pt;")
            layout.addWidget(reason_label)

        return card

    def _clear_history(self) -> None:
        self.history_service.clear("shop_qualified")
        self._refresh_history()

    def _on_start(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return

        mode = "normal" if self.mode_combo.currentIndex() == 0 else "deepnight"
        version = "new" if self.version_combo.currentIndex() == 0 else "old"
        require_double = self.settings.shop_require_double_valid
        stop_currency = int(self.currency_input.text() or 0) if self.currency_input.isVisible() else 0
        sl_target = int(self.target_input.text() or 0) if self.target_input.isVisible() else 0

        # 页面层负责读取当前设置和表单值，再交给后台线程驱动 ShopService。
        self._reset_stats()
        self.worker = ShopWorker(
            self.shop_service,
            mode=mode,
            version=version,
            stop_currency=stop_currency,
            require_double=require_double,
            sl_mode_enabled=self.settings.sl_mode_enabled,
            sl_target=sl_target,
            parent=self,
        )
        self.worker.log_signal.connect(lambda message, level: self.logger.log(level, message))
        self.worker.stats_signal.connect(self.stats_panel.set_values)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.finished_signal.connect(self.worker.deleteLater)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.worker.start()

    def _on_stop(self) -> None:
        self.shop_service.stop()
        self.stop_button.setEnabled(False)
        self.logger.log("WARNING", "已请求停止商店流程")

    def _on_finished(self) -> None:
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(self._ocr_ready)
        self._refresh_history()
        self.worker = None
