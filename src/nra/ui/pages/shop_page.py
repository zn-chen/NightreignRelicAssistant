"""遗物自动购买页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTextEdit,
)


class ShopPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)

        # 左侧: 配置区
        config_panel = QVBoxLayout()

        # 模式选择
        mode_group = QGroupBox("模式")
        mode_layout = QVBoxLayout(mode_group)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("遗物类型:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["普通", "深夜"])
        mode_row.addWidget(self._mode_combo)
        mode_layout.addLayout(mode_row)

        ver_row = QHBoxLayout()
        ver_row.addWidget(QLabel("遗物版本:"))
        self._version_combo = QComboBox()
        self._version_combo.addItems(["新版", "旧版"])
        ver_row.addWidget(self._version_combo)
        mode_layout.addLayout(ver_row)
        config_panel.addWidget(mode_group)

        # 匹配设置
        match_group = QGroupBox("匹配设置")
        match_layout = QVBoxLayout(match_group)
        match_row = QHBoxLayout()
        match_row.addWidget(QLabel("匹配模式:"))
        self._match_combo = QComboBox()
        self._match_combo.addItems(["双有效", "三有效"])
        match_row.addWidget(self._match_combo)
        match_layout.addLayout(match_row)

        build_row = QHBoxLayout()
        build_row.addWidget(QLabel("使用 Build:"))
        self._build_combo = QComboBox()
        build_row.addWidget(self._build_combo)
        match_layout.addLayout(build_row)
        config_panel.addWidget(match_group)

        # 停止条件
        stop_group = QGroupBox("停止条件")
        stop_layout = QVBoxLayout(stop_group)

        currency_row = QHBoxLayout()
        currency_row.addWidget(QLabel("暗痕阈值:"))
        self._currency_threshold = QSpinBox()
        self._currency_threshold.setRange(0, 999999)
        self._currency_threshold.setValue(10000)
        self._currency_threshold.setSingleStep(1000)
        currency_row.addWidget(self._currency_threshold)
        stop_layout.addLayout(currency_row)

        # SL 模式
        self._sl_mode_cb = QCheckBox("启用 SL 模式（存档恢复）")
        stop_layout.addWidget(self._sl_mode_cb)

        sl_row = QHBoxLayout()
        sl_row.addWidget(QLabel("目标合格数:"))
        self._sl_target = QSpinBox()
        self._sl_target.setRange(0, 999)
        self._sl_target.setValue(0)
        sl_row.addWidget(self._sl_target)
        stop_layout.addLayout(sl_row)
        config_panel.addWidget(stop_group)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("开始筛选")
        self._start_btn.setMinimumHeight(40)
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setMinimumHeight(40)
        self._stop_btn.setEnabled(False)
        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._stop_btn)
        config_panel.addLayout(btn_layout)

        config_panel.addStretch()
        layout.addLayout(config_panel, 1)

        # 右侧: 日志 + 统计
        right_panel = QVBoxLayout()

        # 统计
        stats_group = QGroupBox("统计")
        stats_layout = QHBoxLayout(stats_group)
        self._stat_labels = {}
        for name in ["购买", "合格", "不合格", "售出"]:
            stat = QVBoxLayout()
            count_label = QLabel("0")
            count_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
            stat.addWidget(count_label)
            stat.addWidget(QLabel(name))
            stats_layout.addLayout(stat)
            self._stat_labels[name] = count_label
        right_panel.addWidget(stats_group)

        # 日志
        right_panel.addWidget(QLabel("日志:"))
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        right_panel.addWidget(self._log_text)

        layout.addLayout(right_panel, 2)
