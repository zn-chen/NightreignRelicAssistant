"""角色构筑管理页面"""

from __future__ import annotations

import json
from PySide6.QtWidgets import (
    QTabWidget, QInputDialog, QMessageBox, QFileDialog,
    QHBoxLayout, QPushButton, QListWidgetItem, QWidget,
    QLabel, QDialog, QDialogButtonBox, QListWidget,
)
from PySide6.QtCore import Qt

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor
from nra.ui.widgets.helpers import make_title
from nra.ui.widgets.list_detail_layout import ListDetailLayout


class BuildPage(ListDetailLayout):

    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        self._pm = preset_manager
        self._vl = vocab_loader
        self._current_build_id: str | None = None
        super().__init__(parent)
        self._setup()
        self._refresh_list()

    def _setup(self):
        # 左侧标题行: 标题 + ↓导出 ↑导入 + 新建
        title_row = QHBoxLayout()
        title_row.addWidget(make_title("构筑列表"))
        title_row.addStretch()

        btn_style = "font-size: 16px; border: none; padding: 2px;"

        export_btn = QPushButton("↑")
        export_btn.setFixedSize(28, 28)
        export_btn.setStyleSheet(btn_style)
        export_btn.setToolTip("导出")
        export_btn.clicked.connect(self._on_export)
        title_row.addWidget(export_btn)

        import_btn = QPushButton("↓")
        import_btn.setFixedSize(28, 28)
        import_btn.setStyleSheet(btn_style)
        import_btn.setToolTip("导入")
        import_btn.clicked.connect(self._on_import)
        title_row.addWidget(import_btn)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setStyleSheet("font-size: 18px; font-weight: bold; border: none; padding: 2px;")
        add_btn.setToolTip("新建构筑")
        add_btn.clicked.connect(self._on_add)
        title_row.addWidget(add_btn)

        self._left_layout.insertLayout(0, title_row)

        self._list.currentRowChanged.connect(self._on_selection_changed)

        # 右侧
        rl = self._right_layout

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

    # ── 列表项 (带删除按钮) ──

    def _make_list_item_widget(self, name: str, build_id: str) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        label = QLabel(name)
        layout.addWidget(label, 1)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet("border: none; font-size: 16px; color: gray;")
        del_btn.setToolTip("删除")
        del_btn.clicked.connect(lambda _, bid=build_id: self._on_delete_by_id(bid))
        layout.addWidget(del_btn)

        return widget

    def refresh_group_refs(self):
        pass

    # ── 列表操作 ──

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for b in self._pm.builds:
            item = QListWidgetItem()
            widget = self._make_list_item_widget(b["name"], b["id"])
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
        self._list.blockSignals(False)

    def _on_selection_changed(self, row: int):
        if row < 0 or row >= len(self._pm.builds):
            self._current_build_id = None
            self._hide_right()
            return
        build = self._pm.builds[row]
        self._current_build_id = build["id"]
        self._show_right()

        self._normal_editor.set_affixes(build.get("normal_whitelist", []))
        self._deepnight_editor.set_affixes(build.get("deepnight_whitelist", []))
        self._deepnight_neg_editor.set_affixes(build.get("deepnight_neg_whitelist", []))
        self._blacklist_editor.set_affixes(build.get("blacklist", []))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "新建构筑", "构筑名称:")
        if not ok or not name.strip():
            return
        self._pm.create_build(name.strip())
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_delete_by_id(self, build_id: str):
        build = self._pm.get_build(build_id)
        if build is None:
            return
        answer = QMessageBox.question(self, "确认删除",
            f"确定删除构筑 \"{build['name']}\" 吗？")
        if answer != QMessageBox.Yes:
            return
        self._pm.delete_build(build_id)
        if self._current_build_id == build_id:
            self._current_build_id = None
            self._hide_right()
        self._refresh_list()

    # ── 导出 (弹窗多选) ──

    def _on_export(self):
        if not self._pm.builds:
            QMessageBox.information(self, "提示", "没有可导出的构筑")
            return

        # 弹出多选对话框
        dlg = QDialog(self)
        dlg.setWindowTitle("选择要导出的构筑")
        dlg.resize(300, 400)
        dlg_layout = QVBoxLayout(dlg)

        select_list = QListWidget()
        select_list.setSelectionMode(QListWidget.MultiSelection)
        for b in self._pm.builds:
            select_list.addItem(b["name"])
        # 默认全选
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

        selected_builds = [self._pm.builds[r] for r in selected_rows]
        export_data = [{k: v for k, v in b.items() if k not in ("id", "common_group_ids")} for b in selected_builds]

        if len(export_data) == 1:
            default_name = f"{export_data[0]['name']}.json"
        else:
            default_name = "builds.json"

        path, _ = QFileDialog.getSaveFileName(self, "导出构筑", default_name, "JSON (*.json)")
        if not path:
            return

        out = export_data if len(export_data) > 1 else export_data[0]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    # ── 导入 ──

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入构筑", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 支持单个或数组
        items = data if isinstance(data, list) else [data]
        for item in items:
            name = item.get("name", "导入的构筑")
            build = self._pm.create_build(name)
            self._pm.update_build(build["id"], **{k: v for k, v in item.items() if k in build and k != "id"})
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    # ── 自动保存 ──

    def _on_normal_changed(self, affixes):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, normal_whitelist=affixes)

    def _on_deepnight_changed(self, affixes):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, deepnight_whitelist=affixes)

    def _on_deepnight_neg_changed(self, affixes):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, deepnight_neg_whitelist=affixes)

    def _on_blacklist_changed(self, affixes):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, blacklist=affixes)
