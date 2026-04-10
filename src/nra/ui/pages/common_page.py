"""通用词条组管理页面"""

from __future__ import annotations

import json
from PySide6.QtWidgets import (
    QLineEdit, QTabWidget,
    QInputDialog, QMessageBox, QFileDialog,
)

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor
from nra.ui.widgets.helpers import make_title
from nra.ui.widgets.list_detail_layout import ListDetailLayout


class CommonPage(ListDetailLayout):

    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        self._pm = preset_manager
        self._vl = vocab_loader
        self._current_group_id: str | None = None
        super().__init__(parent)
        self._setup()
        self._refresh_list()

    def _setup(self):
        # 左侧
        self._left_layout.insertWidget(0, make_title("通用词条组"))
        self._list.currentRowChanged.connect(self._on_selection_changed)
        self._add_left_buttons(
            [("新建", self._on_add), ("删除", self._on_delete)],
            [("导出", self._on_export_single), ("导入", self._on_import_single)],
            [("批量导出", self._on_export_all), ("批量导入", self._on_import_all)],
        )

        # 右侧
        rl = self._right_layout

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("组名称")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        rl.addWidget(self._name_edit)

        normal_vocab = self._vl.load(["normal.txt", "normal_special.txt"])
        deepnight_pos_vocab = self._vl.load(["deepnight_pos.txt"])
        deepnight_neg_vocab = self._vl.load(["deepnight_neg.txt"])
        all_vocab = self._vl.load(["normal.txt", "normal_special.txt", "deepnight_pos.txt", "deepnight_neg.txt"])

        self._tabs = QTabWidget()

        self._normal_editor = AffixEditor(normal_vocab)
        self._normal_editor.affixes_changed.connect(self._on_normal_changed)
        self._tabs.addTab(self._normal_editor, "普通白名单")

        self._deepnight_editor = AffixEditor(deepnight_pos_vocab)
        self._deepnight_editor.affixes_changed.connect(self._on_deepnight_changed)
        self._tabs.addTab(self._deepnight_editor, "深夜正面")

        self._deepnight_neg_editor = AffixEditor(deepnight_neg_vocab)
        self._deepnight_neg_editor.affixes_changed.connect(self._on_deepnight_neg_changed)
        self._tabs.addTab(self._deepnight_neg_editor, "深夜负面")

        self._blacklist_editor = AffixEditor(all_vocab)
        self._blacklist_editor.affixes_changed.connect(self._on_blacklist_changed)
        self._tabs.addTab(self._blacklist_editor, "黑名单")

        rl.addWidget(self._tabs)

    # ── 列表操作 ──

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for g in self._pm.common_groups:
            self._list.addItem(g["name"])
        self._list.blockSignals(False)

    def _on_selection_changed(self, row: int):
        if row < 0 or row >= len(self._pm.common_groups):
            self._current_group_id = None
            self._hide_right()
            return
        group = self._pm.common_groups[row]
        self._current_group_id = group["id"]
        self._show_right()
        self._name_edit.setText(group["name"])
        self._normal_editor.set_affixes(group.get("normal_affixes", []))
        self._deepnight_editor.set_affixes(group.get("deepnight_affixes", []))
        self._deepnight_neg_editor.set_affixes(group.get("deepnight_neg_affixes", []))
        self._blacklist_editor.set_affixes(group.get("blacklist_affixes", []))

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
        answer = QMessageBox.question(self, "确认删除",
            f"确定删除通用词条组 \"{group['name']}\" 吗？\n引用此组的 构筑 将自动解除关联。")
        if answer != QMessageBox.Yes:
            return
        self._pm.delete_common_group(group["id"])
        self._current_group_id = None
        self._hide_right()
        self._refresh_list()

    # ── 导入导出 ──

    def _group_export_data(self, group: dict) -> dict:
        return {k: v for k, v in group.items() if k != "id"}

    def _on_export_single(self):
        row = self._list.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一个通用组")
            return
        group = self._pm.common_groups[row]
        path, _ = QFileDialog.getSaveFileName(self, "导出通用组",
            f"{group['name']}.json", "JSON (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._group_export_data(group), f, ensure_ascii=False, indent=2)

    def _on_import_single(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入通用组", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("name", "导入的通用组")
        group = self._pm.create_common_group(name)
        self._pm.update_common_group(group["id"], **{k: v for k, v in data.items() if k in group and k != "id"})
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_export_all(self):
        if not self._pm.common_groups:
            QMessageBox.information(self, "提示", "没有可导出的通用组")
            return
        path, _ = QFileDialog.getSaveFileName(self, "批量导出通用组",
            "common_groups.json", "JSON (*.json)")
        if not path:
            return
        data = [self._group_export_data(g) for g in self._pm.common_groups]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _on_import_all(self):
        path, _ = QFileDialog.getOpenFileName(self, "批量导入通用组", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            QMessageBox.warning(self, "格式错误", "批量导入需要 JSON 数组格式")
            return
        for item in data:
            name = item.get("name", "导入的通用组")
            group = self._pm.create_common_group(name)
            self._pm.update_common_group(group["id"], **{k: v for k, v in item.items() if k in group and k != "id"})
        self._refresh_list()

    # ── 自动保存 ──

    def _on_name_changed(self):
        if self._current_group_id is None:
            return
        new_name = self._name_edit.text().strip()
        if not new_name:
            return
        self._pm.update_common_group(self._current_group_id, name=new_name)
        row = self._list.currentRow()
        if row >= 0:
            self._list.item(row).setText(new_name)

    def _on_normal_changed(self, affixes):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, normal_affixes=affixes)

    def _on_deepnight_changed(self, affixes):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, deepnight_affixes=affixes)

    def _on_deepnight_neg_changed(self, affixes):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, deepnight_neg_affixes=affixes)

    def _on_blacklist_changed(self, affixes):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, blacklist_affixes=affixes)
