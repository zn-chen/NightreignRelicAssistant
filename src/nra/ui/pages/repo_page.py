"""仓库整理页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTextEdit,
)


class RepoPage(QWidget):
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

        clean_row = QHBoxLayout()
        clean_row.addWidget(QLabel("清理模式:"))
        self._clean_mode_combo = QComboBox()
        self._clean_mode_combo.addItems(["售出", "收藏"])
        clean_row.addWidget(self._clean_mode_combo)
        mode_layout.addLayout(clean_row)
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

        # 数量设置
        count_group = QGroupBox("数量设置")
        count_layout = QVBoxLayout(count_group)
        self._auto_detect_cb = QCheckBox("自动检测遗物数量")
        self._auto_detect_cb.setChecked(True)
        count_layout.addWidget(self._auto_detect_cb)

        max_row = QHBoxLayout()
        max_row.addWidget(QLabel("最大检测数量:"))
        self._max_count = QSpinBox()
        self._max_count.setRange(0, 999)
        self._max_count.setValue(0)
        max_row.addWidget(self._max_count)
        count_layout.addLayout(max_row)

        self._allow_favorited_cb = QCheckBox("允许操作已收藏遗物")
        count_layout.addWidget(self._allow_favorited_cb)
        config_panel.addWidget(count_group)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("开始清理")
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
        for name in ["检测", "合格", "不合格", "跳过", "售出", "收藏"]:
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
