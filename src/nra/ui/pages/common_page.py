"""通用词条组管理页面"""

from __future__ import annotations

import json
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QListWidgetItem
from qfluentwidgets import (
    PushButton, BodyLabel, MessageBox, ListWidget, TabWidget,
)

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor
from nra.ui.widgets.helpers import make_title, make_card
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
        # 左侧标题行
        title_row = QHBoxLayout()
        title_row.addWidget(make_title("通用词条组"))
        title_row.addStretch()

        export_btn = PushButton("↑")
        export_btn.setFixedSize(28, 28)
        export_btn.setToolTip("导出")
        export_btn.clicked.connect(self._on_export)
        title_row.addWidget(export_btn)

        import_btn = PushButton("↓")
        import_btn.setFixedSize(28, 28)
        import_btn.setToolTip("导入")
        import_btn.clicked.connect(self._on_import)
        title_row.addWidget(import_btn)

        add_btn = PushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("新建通用组")
        add_btn.clicked.connect(self._on_add)
        title_row.addWidget(add_btn)

        self._left_layout.insertLayout(0, title_row)
        self._list.currentRowChanged.connect(self._on_selection_changed)

        # 右侧
        rl = self._right_layout

        from qfluentwidgets import LineEdit
        name_card, name_layout = make_card("名称")
        self._name_edit = LineEdit()
        self._name_edit.setPlaceholderText("组名称")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        name_layout.addWidget(self._name_edit)
        rl.addWidget(name_card)

        affix_card, affix_layout = make_card("词条配置")

        normal_vocab = self._vl.load(["normal.txt", "normal_special.txt"])
        deepnight_pos_vocab = self._vl.load(["deepnight_pos.txt"])
        deepnight_neg_vocab = self._vl.load(["deepnight_neg.txt"])
        all_vocab = self._vl.load(["normal.txt", "normal_special.txt", "deepnight_pos.txt", "deepnight_neg.txt"])

        self._tabs = TabWidget()

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

        affix_layout.addWidget(self._tabs)
        rl.addWidget(affix_card, 1)

    # ── 列表项 ──

    def _make_list_item_widget(self, name: str, group_id: str) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        label = BodyLabel(name)
        layout.addWidget(label, 1)
        del_btn = PushButton("×")
        del_btn.setFixedSize(22, 22)
        del_btn.setToolTip("删除")
        del_btn.clicked.connect(lambda _, gid=group_id: self._on_delete_by_id(gid))
        layout.addWidget(del_btn)
        return widget

    # ── 列表操作 ──

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for g in self._pm.common_groups:
            item = QListWidgetItem()
            widget = self._make_list_item_widget(g["name"], g["id"])
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
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
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建通用词条组", "组名:")
        if not ok or not name.strip():
            return
        self._pm.create_common_group(name.strip())
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_delete_by_id(self, group_id: str):
        group = self._pm.get_common_group(group_id)
        if group is None:
            return
        w = MessageBox("确认删除",
            f"确定删除通用词条组 \"{group['name']}\" 吗？\n引用此组的构筑将自动解除关联。", self)
        if not w.exec():
            return
        self._pm.delete_common_group(group_id)
        if self._current_group_id == group_id:
            self._current_group_id = None
            self._hide_right()
        self._refresh_list()

    # ── 导出 ──

    def _on_export(self):
        if not self._pm.common_groups:
            return
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog

        dlg = QDialog(self)
        dlg.setWindowTitle("选择要导出的通用组")
        dlg.resize(300, 400)
        dlg_layout = QVBoxLayout(dlg)
        select_list = ListWidget()
        select_list.setSelectionMode(ListWidget.MultiSelection)
        for g in self._pm.common_groups:
            select_list.addItem(g["name"])
        select_list.selectAll()
        dlg_layout.addWidget(select_list)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        dlg_layout.addWidget(buttons)

        if dlg.exec() != QDialog.Accepted:
            return
        selected_rows = [select_list.row(item) for item in select_list.selectedItems()]
        if not selected_rows:
            return

        selected = [self._pm.common_groups[r] for r in selected_rows]
        data = [{k: v for k, v in g.items() if k != "id"} for g in selected]
        default_name = f"{data[0]['name']}.json" if len(data) == 1 else "common_groups.json"

        path, _ = QFileDialog.getSaveFileName(self, "导出通用组", default_name, "JSON (*.json)")
        if not path:
            return
        out = data if len(data) > 1 else data[0]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    # ── 导入 ──

    def _on_import(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "导入通用组", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else [data]
        for item in items:
            name = item.get("name", "导入的通用组")
            group = self._pm.create_common_group(name)
            self._pm.update_common_group(group["id"], **{k: v for k, v in item.items() if k in group and k != "id"})
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    # ── 自动保存 ──

    def _on_name_changed(self):
        if self._current_group_id is None:
            return
        new_name = self._name_edit.text().strip()
        if not new_name:
            return
        self._pm.update_common_group(self._current_group_id, name=new_name)
        self._refresh_list()
        for i, g in enumerate(self._pm.common_groups):
            if g["id"] == self._current_group_id:
                self._list.setCurrentRow(i)
                break

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
