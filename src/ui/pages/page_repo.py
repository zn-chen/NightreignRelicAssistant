"""仓库清理页。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QCheckBox, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QTabWidget, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, PrimaryPushButton, PushButton

from core.models.runtime import AppSettings
from services.history_service import HistoryService
from services.repo_service import RepoService
from ui.components import LoggerWidget, StableComboBox, StatsPanel
from ui.workers.repo_worker import RepoWorker


class RepoPage(QWidget):
    def __init__(self, history_service: HistoryService, repo_service: RepoService, parent=None):
        super().__init__(parent)
        self.setObjectName("RepoPage")
        self.history_service = history_service
        self.repo_service = repo_service
        self.settings = AppSettings()
        self.worker: RepoWorker | None = None
        self._ocr_ready = False

        self.logger = LoggerWidget(self)
        self.stats_panel = StatsPanel(["已检测", "合格", "不合格", "已售出"])

        self._records_container = QWidget(self)
        self._records_layout = QVBoxLayout(self._records_container)
        self._records_layout.setContentsMargins(0, 0, 0, 0)
        self._records_layout.setSpacing(6)

        self._init_ui()
        self._refresh_history()
        self._reset_stats()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(6)

        title = QLabel("仓库清理")
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
        layout.addWidget(QLabel("清理:"))
        self.clean_mode_combo = StableComboBox(card)
        self.clean_mode_combo.addItems(["售出", "收藏"])
        self.clean_mode_combo.setFixedWidth(100)
        self.clean_mode_combo.currentIndexChanged.connect(self._on_clean_mode_changed)
        layout.addWidget(self.clean_mode_combo)

        layout.addSpacing(10)
        layout.addWidget(QLabel("数量:"))
        self.max_input = QLineEdit(card)
        self.max_input.setText("100")
        self.max_input.setFixedWidth(100)
        self.max_input.setFixedHeight(33)
        self.max_input.setValidator(QIntValidator(1, 2000, self))
        self.max_input.setPlaceholderText("1-2000")
        self.max_input.setVisible(False)
        layout.addWidget(self.max_input)

        self.auto_detect_checkbox = QCheckBox("自动检测", card)
        self.auto_detect_checkbox.setChecked(True)
        self.auto_detect_checkbox.stateChanged.connect(self._on_auto_detect_changed)
        layout.addWidget(self.auto_detect_checkbox)

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

        self.records_group = QGroupBox(dashboard)
        group_layout = QVBoxLayout(self.records_group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(4)

        clear_button = PushButton("清空记录", self.records_group)
        clear_button.clicked.connect(self._clear_history)
        group_layout.addWidget(clear_button)

        scroll = QScrollArea(self.records_group)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._records_container)
        group_layout.addWidget(scroll)

        layout.addWidget(self.records_group, 1)
        self._update_records_title()
        return dashboard

    def set_ocr_ready(self, ready: bool) -> None:
        self._ocr_ready = ready
        self.start_button.setEnabled(ready)
        self.start_button.setText("开始清理" if ready else "初始化OCR...")

    def update_settings(self, settings: AppSettings) -> None:
        self.settings = settings

    def _reset_stats(self) -> None:
        self.stats_panel.set_values({"已检测": 0, "合格": 0, "不合格": 0, "已售出": 0})

    def _history_bucket(self) -> str:
        # 当前日志面板展示哪个桶，完全由“售出 / 收藏”模式决定。
        return "repo_sold" if self.clean_mode_combo.currentIndex() == 0 else "repo_favorited"

    def _update_records_title(self) -> None:
        title = "已售出遗物词条" if self.clean_mode_combo.currentIndex() == 0 else "已收藏遗物词条"
        self.records_group.setTitle(title)

    def _refresh_history(self) -> None:
        # 每次刷新都重建记录列表，保证切换模式后不会残留另一类历史项。
        while self._records_layout.count():
            item = self._records_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        records = list(reversed(self.history_service.list_records(self._history_bucket())))
        if not records:
            placeholder = QLabel("暂无遗物记录", self._records_container)
            placeholder.setStyleSheet("color: gray; padding: 12px 0;")
            placeholder.setAlignment(Qt.AlignCenter)
            self._records_layout.addWidget(placeholder)
            return

        for record in records[:30]:
            self._records_layout.addWidget(self._build_record_card(record))
        self._records_layout.addStretch(1)

    def _build_record_card(self, record: dict) -> QWidget:
        card = CardWidget(self._records_container)
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

        extra = record.get("extra", {})
        reason = extra.get("reason")
        relic_state = extra.get("relic_state")
        details = []
        if relic_state:
            details.append(f"状态: {relic_state}")
        if reason:
            details.append(str(reason))
        if details:
            detail_label = QLabel("  ·  ".join(details), card)
            detail_label.setWordWrap(True)
            detail_label.setStyleSheet("color: #777; font-size: 9pt;")
            layout.addWidget(detail_label)

        return card

    def _clear_history(self) -> None:
        self.history_service.clear(self._history_bucket())
        self._refresh_history()

    def _on_auto_detect_changed(self) -> None:
        self.max_input.setVisible(not self.auto_detect_checkbox.isChecked())

    def _on_clean_mode_changed(self) -> None:
        self._update_records_title()
        self._refresh_history()

    def _on_start(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return

        mode = "normal" if self.mode_combo.currentIndex() == 0 else "deepnight"
        cleaning_mode = "售出" if self.clean_mode_combo.currentIndex() == 0 else "收藏"
        max_relics = 0 if self.auto_detect_checkbox.isChecked() else int(self.max_input.text() or 100)
        allow_operate_favorited = self.settings.allow_operate_favorited
        require_double = self.settings.require_double_valid

        # 页面只负责采集参数并启动线程，具体流程编排交给 RepoService。
        self._reset_stats()
        self.worker = RepoWorker(
            self.repo_service,
            mode=mode,
            cleaning_mode=cleaning_mode,
            max_relics=max_relics,
            allow_operate_favorited=allow_operate_favorited,
            require_double=require_double,
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
        self.repo_service.stop()
        self.stop_button.setEnabled(False)
        self.logger.log("WARNING", "已请求停止仓库流程")

    def _on_finished(self) -> None:
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(self._ocr_ready)
        self._refresh_history()
        self.worker = None
