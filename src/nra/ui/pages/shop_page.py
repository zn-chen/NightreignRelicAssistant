"""自动购买页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTextEdit, QLabel,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.helpers import make_card


class ShopPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(16)

        # 左侧: 配置区
        config_panel = QVBoxLayout()
        config_panel.setSpacing(12)

        # 匹配设置
        match_card, match_layout = make_card("匹配设置")
        match_row = QHBoxLayout()
        match_row.addWidget(QLabel("匹配模式:"))
        self._match_combo = QComboBox()
        self._match_combo.addItems(["双有效", "三有效"])
        match_row.addWidget(self._match_combo)
        match_layout.addLayout(match_row)
        config_panel.addWidget(match_card)

        # 停止条件
        stop_card, stop_layout = make_card("停止条件")

        self._no_limit_cb = QCheckBox("不限制")
        self._no_limit_cb.setChecked(True)
        self._no_limit_cb.stateChanged.connect(self._on_no_limit_toggled)
        stop_layout.addWidget(self._no_limit_cb)

        currency_row = QHBoxLayout()
        currency_row.addWidget(QLabel("暗痕阈值:"))
        self._currency_threshold = QSpinBox()
        self._currency_threshold.setRange(0, 999999)
        self._currency_threshold.setValue(10000)
        self._currency_threshold.setSingleStep(1000)
        self._currency_threshold.setEnabled(False)
        currency_row.addWidget(self._currency_threshold)
        stop_layout.addLayout(currency_row)
        config_panel.addWidget(stop_card)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self._start_btn = QPushButton("开始")
        self._start_btn.setMinimumHeight(36)
        self._stop_btn = QPushButton("停止")
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

        # 统计
        stats_card, stats_card_layout = make_card("统计")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        self._stat_labels = {}
        for name in ["购买", "合格", "不合格", "售出"]:
            stat = QVBoxLayout()
            stat.setAlignment(Qt.AlignCenter)
            count_label = QLabel("0")
            count_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            count_label.setAlignment(Qt.AlignCenter)
            stat.addWidget(count_label)
            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("color: gray;")
            stat.addWidget(name_label)
            stats_layout.addLayout(stat)
            self._stat_labels[name] = count_label
        stats_card_layout.addLayout(stats_layout)
        right_panel.addWidget(stats_card)

        # 日志
        log_card, log_layout = make_card("日志")
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        log_layout.addWidget(self._log_text)
        right_panel.addWidget(log_card, 1)

        layout.addLayout(right_panel, 2)

    def _on_no_limit_toggled(self, state):
        self._currency_threshold.setEnabled(not bool(state))
