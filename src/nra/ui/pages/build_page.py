"""角色 Build 管理页面"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QPushButton, QLineEdit,
    QGroupBox, QCheckBox, QSpinBox, QTabWidget,
    QScrollArea, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Qt

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor


class BuildPage(QWidget):
    """角色 Build 管理：左侧列表 + 右侧编辑面板。"""

    def __init__(
        self,
        preset_manager: PresetManager,
        vocab_loader: VocabularyLoader,
        parent=None,
    ):
        super().__init__(parent)
        self._pm = preset_manager
        self._vl = vocab_loader
        self._current_build_id: str | None = None
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
        left_layout.addWidget(QLabel("角色 Build"))

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

        # ── 右侧面板 (QScrollArea) ──────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self._right = QWidget()
        right_layout = QVBoxLayout(self._right)

        # Build 名称
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Build 名称")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        right_layout.addWidget(self._name_edit)

        # 最少命中词条数
        min_row = QHBoxLayout()
        min_row.addWidget(QLabel("最少命中词条数:"))
        self._min_spin = QSpinBox()
        self._min_spin.setRange(1, 6)
        self._min_spin.setValue(2)
        self._min_spin.valueChanged.connect(self._on_min_matches_changed)
        min_row.addWidget(self._min_spin)
        min_row.addStretch()
        right_layout.addLayout(min_row)

        # 引用通用词条组
        self._common_group_box = QGroupBox("引用通用词条组")
        self._common_group_box.setCheckable(True)
        self._common_group_box.setChecked(True)
        self._common_group_box.toggled.connect(self._on_include_common_toggled)
        self._common_group_layout = QVBoxLayout(self._common_group_box)
        right_layout.addWidget(self._common_group_box)

        # 引用黑名单组
        self._blacklist_group_box = QGroupBox("引用黑名单组")
        self._blacklist_group_layout = QVBoxLayout(self._blacklist_group_box)
        right_layout.addWidget(self._blacklist_group_box)

        # 白名单编辑 Tabs
        normal_vocab = self._vl.load(["normal.txt", "normal_special.txt"])
        deepnight_vocab = self._vl.load(["deepnight_pos.txt"])

        self._tabs = QTabWidget()

        self._normal_editor = AffixEditor(normal_vocab)
        self._normal_editor.affixes_changed.connect(self._on_normal_changed)
        self._tabs.addTab(self._normal_editor, "普通白名单")

        self._deepnight_editor = AffixEditor(deepnight_vocab)
        self._deepnight_editor.affixes_changed.connect(self._on_deepnight_changed)
        self._tabs.addTab(self._deepnight_editor, "深夜白名单")

        right_layout.addWidget(self._tabs)

        self._right.setEnabled(False)
        scroll.setWidget(self._right)
        splitter.addWidget(scroll)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # 初始化 group checkboxes
        self._populate_common_checkboxes()
        self._populate_blacklist_checkboxes()

    # ── Group Checkboxes ────────────────────────────────────────

    def _populate_common_checkboxes(self):
        # Clear existing checkboxes
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

    def _populate_blacklist_checkboxes(self):
        while self._blacklist_group_layout.count():
            item = self._blacklist_group_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._blacklist_cbs: list[tuple[str, QCheckBox]] = []
        for group in self._pm.blacklist_groups:
            cb = QCheckBox(group["name"])
            cb.stateChanged.connect(self._on_blacklist_ids_changed)
            self._blacklist_group_layout.addWidget(cb)
            self._blacklist_cbs.append((group["id"], cb))

    def _sync_common_checkboxes(self, build: dict):
        """Sync checkbox state to match build's common_group_ids."""
        checked_ids = set(build.get("common_group_ids", []))
        for gid, cb in self._common_cbs:
            cb.blockSignals(True)
            cb.setChecked(gid in checked_ids)
            cb.blockSignals(False)

    def _sync_blacklist_checkboxes(self, build: dict):
        """Sync checkbox state to match build's blacklist_group_ids."""
        checked_ids = set(build.get("blacklist_group_ids", []))
        for gid, cb in self._blacklist_cbs:
            cb.blockSignals(True)
            cb.setChecked(gid in checked_ids)
            cb.blockSignals(False)

    def refresh_group_refs(self):
        """Refresh group checkboxes when common/blacklist groups change externally."""
        self._populate_common_checkboxes()
        self._populate_blacklist_checkboxes()
        # Re-sync checked state if a build is selected
        if self._current_build_id is not None:
            build = self._pm.get_build(self._current_build_id)
            if build is not None:
                self._sync_common_checkboxes(build)
                self._sync_blacklist_checkboxes(build)

    # ── 列表操作 ─────────────────────────────────────────────────

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for b in self._pm.builds:
            self._list.addItem(b["name"])
        self._list.blockSignals(False)

    def _on_selection_changed(self, row: int):
        if row < 0 or row >= len(self._pm.builds):
            self._current_build_id = None
            self._right.setEnabled(False)
            return
        build = self._pm.builds[row]
        self._current_build_id = build["id"]
        self._right.setEnabled(True)

        self._name_edit.setText(build["name"])

        self._min_spin.blockSignals(True)
        self._min_spin.setValue(build.get("min_matches", 2))
        self._min_spin.blockSignals(False)

        self._common_group_box.blockSignals(True)
        self._common_group_box.setChecked(build.get("include_common", True))
        self._common_group_box.blockSignals(False)

        self._sync_common_checkboxes(build)
        self._sync_blacklist_checkboxes(build)

        self._normal_editor.set_affixes(build.get("normal_whitelist", []))
        self._deepnight_editor.set_affixes(build.get("deepnight_whitelist", []))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "新建 Build", "Build 名称:")
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
        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除 Build \"{build['name']}\" 吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self._pm.delete_build(build["id"])
        self._current_build_id = None
        self._right.setEnabled(False)
        self._refresh_list()

    # ── 自动保存 ─────────────────────────────────────────────────

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
        if self._current_build_id is None:
            return
        self._pm.update_build(self._current_build_id, min_matches=value)

    def _on_include_common_toggled(self, checked: bool):
        if self._current_build_id is None:
            return
        self._pm.update_build(self._current_build_id, include_common=checked)

    def _on_common_ids_changed(self):
        if self._current_build_id is None:
            return
        ids = [gid for gid, cb in self._common_cbs if cb.isChecked()]
        self._pm.update_build(self._current_build_id, common_group_ids=ids)

    def _on_blacklist_ids_changed(self):
        if self._current_build_id is None:
            return
        ids = [gid for gid, cb in self._blacklist_cbs if cb.isChecked()]
        self._pm.update_build(self._current_build_id, blacklist_group_ids=ids)

    def _on_normal_changed(self, affixes: list[str]):
        if self._current_build_id is None:
            return
        self._pm.update_build(self._current_build_id, normal_whitelist=affixes)

    def _on_deepnight_changed(self, affixes: list[str]):
        if self._current_build_id is None:
            return
        self._pm.update_build(self._current_build_id, deepnight_whitelist=affixes)
