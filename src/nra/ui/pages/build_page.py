"""角色 BUILD 管理页面"""

from __future__ import annotations

import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLineEdit,
    QGroupBox, QCheckBox, QSpinBox, QTabWidget,
    QScrollArea, QInputDialog, QMessageBox, QFileDialog,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor
from nra.ui.widgets.helpers import make_title


class BuildPage(QWidget):

    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        super().__init__(parent)
        self._pm = preset_manager
        self._vl = vocab_loader
        self._current_build_id: str | None = None
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # 左侧
        left = QWidget()
        left.setFixedWidth(220)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_layout.addWidget(make_title("BUILD 列表"))

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        add_btn = QPushButton("新建")
        add_btn.clicked.connect(self._on_add)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left_layout.addLayout(btn_row)

        # 导入导出
        io_row = QHBoxLayout()
        io_row.setSpacing(6)
        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self._on_export_single)
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self._on_import_single)
        io_row.addWidget(export_btn)
        io_row.addWidget(import_btn)
        left_layout.addLayout(io_row)

        batch_row = QHBoxLayout()
        batch_row.setSpacing(6)
        batch_export_btn = QPushButton("批量导出")
        batch_export_btn.clicked.connect(self._on_export_all)
        batch_import_btn = QPushButton("批量导入")
        batch_import_btn.clicked.connect(self._on_import_all)
        batch_row.addWidget(batch_export_btn)
        batch_row.addWidget(batch_import_btn)
        left_layout.addLayout(batch_row)

        root.addWidget(left)

        # 右侧
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self._right = QWidget()
        right_layout = QVBoxLayout(self._right)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(12)

        right_layout.addWidget(make_title("BUILD 编辑"))

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("BUILD 名称")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        right_layout.addWidget(self._name_edit)

        min_row = QHBoxLayout()
        min_row.addWidget(make_title("最少命中词条数"))
        self._min_spin = QSpinBox()
        self._min_spin.setRange(1, 6)
        self._min_spin.setValue(2)
        self._min_spin.setFixedWidth(60)
        self._min_spin.valueChanged.connect(self._on_min_matches_changed)
        min_row.addWidget(self._min_spin)
        min_row.addStretch()
        right_layout.addLayout(min_row)

        self._common_group_box = QGroupBox("引用通用词条组")
        self._common_group_box.setCheckable(True)
        self._common_group_box.setChecked(True)
        self._common_group_box.toggled.connect(self._on_include_common_toggled)
        self._common_group_layout = QVBoxLayout(self._common_group_box)
        self._common_group_layout.setSpacing(4)
        right_layout.addWidget(self._common_group_box)

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

        right_layout.addWidget(self._tabs)

        scroll.setWidget(self._right)
        self._scroll = scroll
        self._scroll.setVisible(False)
        root.addWidget(self._scroll, 1)  # stretch=1, 右侧吃掉多余空间

        self._populate_common_checkboxes()

    # ── Group Checkboxes ──

    def _populate_common_checkboxes(self):
        while self._common_group_layout.count():
            item = self._common_group_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._common_cbs: list[tuple[str, QCheckBox]] = []
        for group in self._pm.common_groups:
            cb = QCheckBox(group["name"])
            cb.stateChanged.connect(self._on_common_ids_changed)
            self._common_group_layout.addWidget(cb)
            self._common_cbs.append((group["id"], cb))

    def _sync_common_checkboxes(self, build: dict):
        checked_ids = set(build.get("common_group_ids", []))
        for gid, cb in self._common_cbs:
            cb.blockSignals(True)
            cb.setChecked(gid in checked_ids)
            cb.blockSignals(False)

    def refresh_group_refs(self):
        self._populate_common_checkboxes()
        if self._current_build_id is not None:
            build = self._pm.get_build(self._current_build_id)
            if build is not None:
                self._sync_common_checkboxes(build)

    # ── 列表操作 ──

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for b in self._pm.builds:
            self._list.addItem(b["name"])
        self._list.blockSignals(False)

    def _on_selection_changed(self, row: int):
        if row < 0 or row >= len(self._pm.builds):
            self._current_build_id = None
            self._scroll.setVisible(False)
            return
        build = self._pm.builds[row]
        self._current_build_id = build["id"]
        self._scroll.setVisible(True)

        self._name_edit.setText(build["name"])
        self._min_spin.blockSignals(True)
        self._min_spin.setValue(build.get("min_matches", 2))
        self._min_spin.blockSignals(False)
        self._common_group_box.blockSignals(True)
        self._common_group_box.setChecked(build.get("include_common", True))
        self._common_group_box.blockSignals(False)
        self._sync_common_checkboxes(build)
        self._normal_editor.set_affixes(build.get("normal_whitelist", []))
        self._deepnight_editor.set_affixes(build.get("deepnight_whitelist", []))
        self._deepnight_neg_editor.set_affixes(build.get("deepnight_neg_whitelist", []))
        self._blacklist_editor.set_affixes(build.get("blacklist", []))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "新建 BUILD", "BUILD 名称:")
        if not ok or not name.strip():
            return
        self._pm.create_build(name.strip())
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_delete(self):
        row = self._list.currentRow()
        if row < 0:
            return
        build = self._pm.builds[row]
        answer = QMessageBox.question(self, "确认删除",
            f"确定删除 BUILD \"{build['name']}\" 吗？")
        if answer != QMessageBox.Yes:
            return
        self._pm.delete_build(build["id"])
        self._current_build_id = None
        self._scroll.setVisible(False)
        self._refresh_list()

    # ── 导入导出 ──

    def _build_export_data(self, build: dict) -> dict:
        """提取 build 的可导出数据（去掉 id 和 common_group_ids）"""
        return {k: v for k, v in build.items() if k not in ("id", "common_group_ids")}

    def _on_export_single(self):
        row = self._list.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一个 BUILD")
            return
        build = self._pm.builds[row]
        path, _ = QFileDialog.getSaveFileName(self, "导出 BUILD",
            f"{build['name']}.json", "JSON (*.json)")
        if not path:
            return
        data = self._build_export_data(build)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _on_import_single(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入 BUILD", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("name", "导入的BUILD")
        build = self._pm.create_build(name)
        self._pm.update_build(build["id"], **{k: v for k, v in data.items() if k in build and k != "id"})
        self._refresh_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_export_all(self):
        if not self._pm.builds:
            QMessageBox.information(self, "提示", "没有可导出的 BUILD")
            return
        path, _ = QFileDialog.getSaveFileName(self, "批量导出 BUILD",
            "builds.json", "JSON (*.json)")
        if not path:
            return
        data = [self._build_export_data(b) for b in self._pm.builds]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _on_import_all(self):
        path, _ = QFileDialog.getOpenFileName(self, "批量导入 BUILD", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            QMessageBox.warning(self, "格式错误", "批量导入需要 JSON 数组格式")
            return
        for item in data:
            name = item.get("name", "导入的BUILD")
            build = self._pm.create_build(name)
            self._pm.update_build(build["id"], **{k: v for k, v in item.items() if k in build and k != "id"})
        self._refresh_list()

    # ── 自动保存 ──

    def _on_name_changed(self):
        if self._current_build_id is None:
            return
        new_name = self._name_edit.text().strip()
        if not new_name:
            return
        self._pm.update_build(self._current_build_id, name=new_name)
        row = self._list.currentRow()
        if row >= 0:
            self._list.item(row).setText(new_name)

    def _on_min_matches_changed(self, value: int):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, min_matches=value)

    def _on_include_common_toggled(self, checked: bool):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, include_common=checked)

    def _on_common_ids_changed(self):
        if self._current_build_id:
            ids = [gid for gid, cb in self._common_cbs if cb.isChecked()]
            self._pm.update_build(self._current_build_id, common_group_ids=ids)

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
