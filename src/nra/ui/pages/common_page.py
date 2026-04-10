"""通用词条组管理页面"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QPushButton, QLineEdit,
    QTabWidget, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Qt

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor


class CommonPage(QWidget):
    """通用词条组管理：左侧列表 + 右侧编辑面板。"""

    def __init__(
        self,
        preset_manager: PresetManager,
        vocab_loader: VocabularyLoader,
        parent=None,
    ):
        super().__init__(parent)
        self._pm = preset_manager
        self._vl = vocab_loader
        self._current_group_id: str | None = None
        self._init_ui()
        self._refresh_list()

    # ── UI 初始化 ────────────────────────────────────────────────

    def _init_ui(self):
        splitter = QSplitter(Qt.Horizontal, self)
        root = QHBoxLayout(self)
        root.addWidget(splitter)

        # ── 左侧面板 ─────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("通用词条组"))

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("新建")
        add_btn.clicked.connect(self._on_add)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left)

        # ── 右侧面板 ─────────────────────────────────────────
        self._right = QWidget()
        right_layout = QVBoxLayout(self._right)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("组名")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        right_layout.addWidget(self._name_edit)

        normal_vocab = self._vl.load(["normal.txt", "normal_special.txt"])
        deepnight_vocab = self._vl.load(["deepnight_pos.txt"])

        self._tabs = QTabWidget()

        self._normal_editor = AffixEditor(normal_vocab)
        self._normal_editor.affixes_changed.connect(self._on_normal_changed)
        self._tabs.addTab(self._normal_editor, "普通词条")

        self._deepnight_editor = AffixEditor(deepnight_vocab)
        self._deepnight_editor.affixes_changed.connect(self._on_deepnight_changed)
        self._tabs.addTab(self._deepnight_editor, "深夜词条")

        right_layout.addWidget(self._tabs)

        self._right.setEnabled(False)
        splitter.addWidget(self._right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    # ── 列表操作 ─────────────────────────────────────────────────

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for g in self._pm.common_groups:
            self._list.addItem(g["name"])
        self._list.blockSignals(False)

    def _on_selection_changed(self, row: int):
        if row < 0 or row >= len(self._pm.common_groups):
            self._current_group_id = None
            self._right.setEnabled(False)
            return
        group = self._pm.common_groups[row]
        self._current_group_id = group["id"]
        self._right.setEnabled(True)
        self._name_edit.setText(group["name"])
        self._normal_editor.set_affixes(group.get("normal_affixes", []))
        self._deepnight_editor.set_affixes(group.get("deepnight_affixes", []))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "新建通用词条组", "组名:")
        if not ok or not name.strip():
            return
        self._pm.create_common_group(name.strip())
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_delete(self):
        row = self._list.currentRow()
        if row < 0:
            return
        group = self._pm.common_groups[row]
        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除通用词条组 \"{group['name']}\" 吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self._pm.delete_common_group(group["id"])
        self._current_group_id = None
        self._right.setEnabled(False)
        self._refresh_list()

    # ── 自动保存 ─────────────────────────────────────────────────

    def _on_name_changed(self):
        if self._current_group_id is None:
            return
        new_name = self._name_edit.text().strip()
        if not new_name:
            return
        self._pm.update_common_group(self._current_group_id, name=new_name)
        # 同步更新左侧列表显示
        row = self._list.currentRow()
        if row >= 0:
            self._list.item(row).setText(new_name)

    def _on_normal_changed(self, affixes: list[str]):
        if self._current_group_id is None:
            return
        self._pm.update_common_group(self._current_group_id, normal_affixes=affixes)

    def _on_deepnight_changed(self, affixes: list[str]):
        if self._current_group_id is None:
            return
        self._pm.update_common_group(self._current_group_id, deepnight_affixes=affixes)
