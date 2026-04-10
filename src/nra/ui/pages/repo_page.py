"""仓库整理页面"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (
    ComboBox, SpinBox, PushButton, CheckBox,
    TextEdit, BodyLabel,
)
from nra.ui.widgets.helpers import make_card


class RepoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(16)

        # 左侧
        config_panel = QVBoxLayout()
        config_panel.setSpacing(12)

        match_card, match_layout = make_card("匹配设置")
        match_row = QHBoxLayout()
        match_row.addWidget(BodyLabel("匹配模式:"))
        self._match_combo = ComboBox()
        self._match_combo.addItems(["双有效", "三有效"])
        match_row.addWidget(self._match_combo)
        match_layout.addLayout(match_row)
        config_panel.addWidget(match_card)

        count_card, count_layout = make_card("数量设置")
        self._no_limit_cb = CheckBox("不限制")
        self._no_limit_cb.setChecked(True)
        self._no_limit_cb.stateChanged.connect(self._on_no_limit_toggled)
        count_layout.addWidget(self._no_limit_cb)
        max_row = QHBoxLayout()
        max_row.addWidget(BodyLabel("最大检测数:"))
        self._max_count = SpinBox()
        self._max_count.setRange(1, 999)
        self._max_count.setValue(100)
        self._max_count.setEnabled(False)
        max_row.addWidget(self._max_count)
        count_layout.addLayout(max_row)
        config_panel.addWidget(count_card)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self._start_btn = PushButton("开始清理")
        self._start_btn.setMinimumHeight(36)
        self._stop_btn = PushButton("停止")
        self._stop_btn.setMinimumHeight(36)
        self._stop_btn.setEnabled(False)
        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._stop_btn)
        config_panel.addLayout(btn_layout)

        config_panel.addStretch()
        layout.addLayout(config_panel, 1)

        # 右侧
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        stats_card, stats_card_layout = make_card("统计")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        self._stat_labels = {}
        for name in ["检测", "合格", "不合格", "售出"]:
            stat = QVBoxLayout()
            stat.setAlignment(Qt.AlignCenter)
            count_label = BodyLabel("0")
            count_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            count_label.setAlignment(Qt.AlignCenter)
            stat.addWidget(count_label)
            name_label = BodyLabel(name)
            name_label.setAlignment(Qt.AlignCenter)
            stat.addWidget(name_label)
            stats_layout.addLayout(stat)
            self._stat_labels[name] = count_label
        stats_card_layout.addLayout(stats_layout)
        right_panel.addWidget(stats_card)

        log_card, log_layout = make_card("日志")
        self._log_text = TextEdit()
        self._log_text.setReadOnly(True)
        log_layout.addWidget(self._log_text)
        right_panel.addWidget(log_card, 1)

        layout.addLayout(right_panel, 2)

    def _on_no_limit_toggled(self, state):
        self._max_count.setEnabled(not bool(state))
