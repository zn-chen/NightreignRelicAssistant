"""词条编辑器 — 搜索+添加的复用组件"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
)
from PySide6.QtCore import Signal, Qt


class AffixEditor(QWidget):
    """词条编辑器：搜索词条库 + 添加到已选列表"""

    affixes_changed = Signal(list)

    def __init__(self, vocabulary: list[str], parent=None):
        super().__init__(parent)
        self._vocabulary = vocabulary
        self._selected: list[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 搜索框
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索词条...")
        self._search_input.textChanged.connect(self._on_search)
        layout.addWidget(self._search_input)

        # 搜索结果
        layout.addWidget(QLabel("词条库:"))
        self._result_list = QListWidget()
        self._result_list.setMaximumHeight(200)
        self._result_list.itemDoubleClicked.connect(self._on_add_item)
        layout.addWidget(self._result_list)

        # 已选词条
        selected_header = QHBoxLayout()
        selected_header.addWidget(QLabel("已选词条:"))
        remove_btn = QPushButton("删除选中")
        remove_btn.clicked.connect(self._on_remove)
        selected_header.addWidget(remove_btn)
        layout.addLayout(selected_header)

        self._selected_list = QListWidget()
        self._selected_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self._selected_list)

        # 初始显示全部词条
        self._update_results(self._vocabulary)

    def _on_search(self, text: str):
        if not text:
            self._update_results(self._vocabulary)
        else:
            filtered = [v for v in self._vocabulary if text in v]
            self._update_results(filtered)

    def _update_results(self, vocabs: list[str]):
        self._result_list.clear()
        for v in vocabs:
            if v not in self._selected:
                self._result_list.addItem(v)

    def _on_add_item(self, item: QListWidgetItem):
        text = item.text()
        if text not in self._selected:
            self._selected.append(text)
            self._selected_list.addItem(text)
            self._on_search(self._search_input.text())
            self.affixes_changed.emit(list(self._selected))

    def _on_remove(self):
        for item in self._selected_list.selectedItems():
            self._selected.remove(item.text())
            self._selected_list.takeItem(self._selected_list.row(item))
        self._on_search(self._search_input.text())
        self.affixes_changed.emit(list(self._selected))

    def set_affixes(self, affixes: list[str]):
        """外部设置已选词条（加载数据时用）"""
        self._selected = list(affixes)
        self._selected_list.clear()
        for a in self._selected:
            self._selected_list.addItem(a)
        self._on_search(self._search_input.text())

    def get_affixes(self) -> list[str]:
        return list(self._selected)
