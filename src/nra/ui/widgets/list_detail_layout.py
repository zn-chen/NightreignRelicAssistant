"""左列表 + 右详情 布局模板"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QScrollArea, QFrame, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import Qt


class ListDetailLayout(QWidget):
    """
    左右分栏布局模板:
    - 左侧: 标题 + 列表(撑满) + 按钮区, 固定宽度
    - 右侧: 可滚动详情面板, 撑满剩余宽度, 无选中时隐藏
    - 右侧隐藏时, 左侧靠左对齐不居中
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_base_layout()

    def _init_base_layout(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 20, 12, 12)
        root.setSpacing(12)
        self._root_layout = root

        # ── 左侧面板 ──
        self._left_panel = QWidget()
        self._left_panel.setFixedWidth(220)
        self._left_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self._left_layout = QVBoxLayout(self._left_panel)
        self._left_layout.setContentsMargins(0, 0, 0, 0)
        self._left_layout.setSpacing(8)

        self._list = QListWidget()
        self._left_layout.addWidget(self._list, 1)

        root.addWidget(self._left_panel)

        # ── 右侧面板 ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_layout.setContentsMargins(4, 0, 4, 0)
        self._right_layout.setSpacing(10)

        self._scroll.setWidget(self._right_panel)
        self._scroll.setVisible(False)
        root.addWidget(self._scroll, 1)

        # ── 右侧占位 spacer (右侧隐藏时撑满, 防止左侧居中) ──
        self._placeholder = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        root.addSpacerItem(self._placeholder)

    def _add_left_buttons(self, *rows):
        for row_items in rows:
            row = QHBoxLayout()
            row.setSpacing(6)
            for label, callback in row_items:
                btn = QPushButton(label)
                btn.clicked.connect(callback)
                row.addWidget(btn)
            self._left_layout.addLayout(row)

    def _show_right(self):
        self._scroll.setVisible(True)

    def _hide_right(self):
        self._scroll.setVisible(False)
