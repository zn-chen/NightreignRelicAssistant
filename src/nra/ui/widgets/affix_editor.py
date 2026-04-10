"""词条编辑器 — 搜索+添加的复用组件"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
)
from PySide6.QtCore import Signal


class AffixEditor(QWidget):
    affixes_changed = Signal(list)

    def __init__(self, vocabulary, parent=None):
        super().__init__(parent)
        self._vocabulary = vocabulary
        self._selected = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("输入关键字搜索词条...")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._filter)
        layout.addWidget(self._search)

        vocab_row = QHBoxLayout()
        vocab_label = QLabel("词条库")
        vocab_label.setStyleSheet("font-weight: bold;")
        vocab_row.addWidget(vocab_label)
        vocab_row.addStretch()
        add_btn = QPushButton("添加选中 ↓")
        add_btn.clicked.connect(self._add_selected)
        vocab_row.addWidget(add_btn)
        layout.addLayout(vocab_row)

        self._vocab_list = QListWidget()
        self._vocab_list.setSelectionMode(QListWidget.ExtendedSelection)
        self._vocab_list.setMaximumHeight(200)
        self._vocab_list.itemDoubleClicked.connect(self._add_item)
        layout.addWidget(self._vocab_list)

        selected_row = QHBoxLayout()
        sel_label = QLabel("已选词条")
        sel_label.setStyleSheet("font-weight: bold;")
        selected_row.addWidget(sel_label)
        selected_row.addStretch()
        del_btn = QPushButton("删除选中")
        del_btn.clicked.connect(self._remove_selected)
        selected_row.addWidget(del_btn)
        layout.addLayout(selected_row)

        self._selected_list = QListWidget()
        self._selected_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self._selected_list)

        self._refresh_vocab()

    def _filter(self, text):
        self._refresh_vocab(text)

    def _refresh_vocab(self, query=""):
        self._vocab_list.clear()
        for v in self._vocabulary:
            if v not in self._selected and (not query or query in v):
                self._vocab_list.addItem(v)

    def _add_item(self, item):
        text = item.text()
        if text not in self._selected:
            self._selected.append(text)
            self._selected_list.addItem(text)
            self._refresh_vocab(self._search.text())
            self.affixes_changed.emit(list(self._selected))

    def _add_selected(self):
        items = self._vocab_list.selectedItems()
        if not items:
            return
        for item in items:
            text = item.text()
            if text not in self._selected:
                self._selected.append(text)
                self._selected_list.addItem(text)
        self._refresh_vocab(self._search.text())
        self.affixes_changed.emit(list(self._selected))

    def _remove_selected(self):
        for item in self._selected_list.selectedItems():
            self._selected.remove(item.text())
            self._selected_list.takeItem(self._selected_list.row(item))
        self._refresh_vocab(self._search.text())
        self.affixes_changed.emit(list(self._selected))

    def set_affixes(self, affixes):
        self._selected = list(affixes)
        self._selected_list.clear()
        for a in self._selected:
            self._selected_list.addItem(a)
        self._refresh_vocab(self._search.text())

    def get_affixes(self):
        return list(self._selected)
