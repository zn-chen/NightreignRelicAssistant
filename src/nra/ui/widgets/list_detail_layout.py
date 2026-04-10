"""左列表 + 右详情 布局模板"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt


class ListDetailLayout(QWidget):
    """
    左右分栏布局模板:
    - 左侧: 标题 + 列表 + 按钮区 (固定宽度, 左对齐)
    - 右侧: 可滚动详情面板 (无选中时隐藏, 选中后展开)

    子类需要:
    1. 调用 _setup_left() 设置左侧标题和按钮
    2. 调用 _setup_right() 获取右侧 layout 并填充内容
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_base_layout()

    def _init_base_layout(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        # 左侧面板
        self._left_panel = QWidget()
        self._left_panel.setFixedWidth(220)
        self._left_layout = QVBoxLayout(self._left_panel)
        self._left_layout.setContentsMargins(0, 0, 0, 0)
        self._left_layout.setSpacing(8)

        # 列表
        self._list = QListWidget()
        self._left_layout.addWidget(self._list)

        root.addWidget(self._left_panel, 0, Qt.AlignLeft | Qt.AlignTop)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        self._separator = separator
        self._separator.setVisible(False)
        root.addWidget(separator)

        # 右侧面板 (QScrollArea)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_layout.setContentsMargins(16, 0, 0, 0)
        self._right_layout.setSpacing(10)

        scroll.setWidget(self._right_panel)
        self._scroll = scroll
        self._scroll.setVisible(False)
        root.addWidget(self._scroll, 1)

        # 弹性空间 — 右侧隐藏时把左侧顶到左边
        self._spacer_stretch = root.addStretch(1)

    def _add_left_buttons(self, *rows):
        """添加按钮行到左侧面板底部, 每个 row 是 [(label, callback), ...]"""
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
        self._separator.setVisible(True)

    def _hide_right(self):
        self._scroll.setVisible(False)
        self._separator.setVisible(False)
