"""自动购买页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTextEdit, QLabel,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.cards import make_card


class ShopPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 左侧
        left = QVBoxLayout()
        left.setSpacing(12)

        match_card, ml = make_card("匹配设置")
        row = QHBoxLayout()
        row.addWidget(QLabel("匹配模式:"))
        self._match = QComboBox()
        self._match.addItems(["双有效", "三有效"])
        row.addWidget(self._match)
        ml.addLayout(row)
        left.addWidget(match_card)

        stop_card, sl = make_card("停止条件")
        self._no_limit = QCheckBox("不限制")
        self._no_limit.setChecked(True)
        self._no_limit.toggled.connect(lambda c: self._threshold.setEnabled(not c))
        sl.addWidget(self._no_limit)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("暗痕阈值:"))
        self._threshold = QSpinBox()
        self._threshold.setRange(0, 999999)
        self._threshold.setValue(10000)
        self._threshold.setSingleStep(1000)
        self._threshold.setEnabled(False)
        row2.addWidget(self._threshold)
        sl.addLayout(row2)
        left.addWidget(stop_card)

        btns = QHBoxLayout()
        self._start = QPushButton("开始")
        self._start.setMinimumHeight(36)
        self._stop = QPushButton("停止")
        self._stop.setMinimumHeight(36)
        self._stop.setEnabled(False)
        btns.addWidget(self._start)
        btns.addWidget(self._stop)
        left.addLayout(btns)
        left.addStretch()
        layout.addLayout(left, 1)

        # 右侧
        right = QVBoxLayout()
        right.setSpacing(12)

        stats_card, stl = make_card("统计")
        stats_row = QHBoxLayout()
        self._stats = {}
        for name in ["购买", "合格", "不合格", "售出"]:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignCenter)
            num = QLabel("0")
            num.setStyleSheet("font-size: 20px; font-weight: bold;")
            num.setAlignment(Qt.AlignCenter)
            col.addWidget(num)
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            col.addWidget(lbl)
            stats_row.addLayout(col)
            self._stats[name] = num
        stl.addLayout(stats_row)
        right.addWidget(stats_card)

        log_card, ll = make_card("日志")
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        ll.addWidget(self._log)
        right.addWidget(log_card, 1)

        layout.addLayout(right, 2)
