"""构筑管理页面"""

import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTabWidget, QScrollArea,
    QInputDialog, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QSizePolicy, QSpacerItem, QFrame,
)
from PySide6.QtCore import Qt

from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor
from nra.ui.widgets.cards import make_card


class BuildPage(QWidget):
    def __init__(self, pm, vl, parent=None):
        super().__init__(parent)
        self._pm = pm
        self._vl = vl
        self._current_id = None
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # 左侧
        left = QWidget()
        left.setFixedWidth(220)
        left.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(10)

        title_row = QHBoxLayout()
        t = QLabel("构筑列表")
        t.setStyleSheet("font-size: 15px; font-weight: bold;")
        title_row.addWidget(t)
        title_row.addStretch()

        for text, handler in [("↑", self._on_export), ("↓", self._on_import), ("+", self._on_add)]:
            btn = QPushButton(text)
            btn.setFixedSize(28, 28)
            btn.clicked.connect(handler)
            title_row.addWidget(btn)

        ll.addLayout(title_row)

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selected)
        ll.addWidget(self._list, 1)

        root.addWidget(left)

        # 右侧
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(10)

        card, cl = make_card("词条配置")
        nv = self._vl.load(["normal.txt", "normal_special.txt"])
        dp = self._vl.load(["deepnight_pos.txt"])
        dn = self._vl.load(["deepnight_neg.txt"])
        av = self._vl.load(["normal.txt", "normal_special.txt", "deepnight_pos.txt", "deepnight_neg.txt"])

        self._tabs = QTabWidget()
        self._editors = {}
        for label, vocab, key in [
            ("普通白名单", nv, "normal_whitelist"),
            ("深夜正面", dp, "deepnight_whitelist"),
            ("深夜负面", dn, "deepnight_neg_whitelist"),
            ("黑名单", av, "blacklist"),
        ]:
            editor = AffixEditor(vocab)
            editor.affixes_changed.connect(lambda aff, k=key: self._save_affixes(k, aff))
            self._tabs.addTab(editor, label)
            self._editors[key] = editor

        cl.addWidget(self._tabs)
        rl.addWidget(card, 1)

        self._scroll.setWidget(right)
        self._scroll.setVisible(False)
        root.addWidget(self._scroll, 1)

        self._spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        root.addSpacerItem(self._spacer)

    def _make_item_widget(self, name, build_id):
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)
        h.addWidget(QLabel(name), 1)
        btn = QPushButton("×")
        btn.setFixedSize(22, 22)
        btn.clicked.connect(lambda _, bid=build_id: self._on_delete(bid))
        h.addWidget(btn)
        return w

    def _refresh_list(self):
        self._list.blockSignals(True)
        self._list.clear()
        for b in self._pm.builds:
            item = QListWidgetItem()
            widget = self._make_item_widget(b["name"], b["id"])
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
        self._list.blockSignals(False)

    def _on_selected(self, row):
        if row < 0 or row >= len(self._pm.builds):
            self._current_id = None
            self._scroll.setVisible(False)
            return
        b = self._pm.builds[row]
        self._current_id = b["id"]
        self._scroll.setVisible(True)
        for key, editor in self._editors.items():
            editor.set_affixes(b.get(key, []))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "新建构筑", "名称:")
        if ok and name.strip():
            self._pm.create_build(name.strip())
            self._refresh_list()
            self._list.setCurrentRow(self._list.count() - 1)

    def _on_delete(self, build_id):
        b = self._pm.get_build(build_id)
        if not b:
            return
        if QMessageBox.question(self, "确认", f"删除 \"{b['name']}\"？") != QMessageBox.Yes:
            return
        self._pm.delete_build(build_id)
        if self._current_id == build_id:
            self._current_id = None
            self._scroll.setVisible(False)
        self._refresh_list()

    def _save_affixes(self, key, affixes):
        if self._current_id:
            self._pm.update_build(self._current_id, **{key: affixes})

    def _on_export(self):
        if not self._pm.builds:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("选择导出")
        dlg.resize(300, 400)
        dl = QVBoxLayout(dlg)
        sel = QListWidget()
        sel.setSelectionMode(QListWidget.MultiSelection)
        for b in self._pm.builds:
            sel.addItem(b["name"])
        sel.selectAll()
        dl.addWidget(sel)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        dl.addWidget(btns)
        if dlg.exec() != QDialog.Accepted:
            return
        rows = [sel.row(i) for i in sel.selectedItems()]
        if not rows:
            return
        data = [{k: v for k, v in self._pm.builds[r].items() if k not in ("id", "common_group_ids")} for r in rows]
        name = f"{data[0]['name']}.json" if len(data) == 1 else "builds.json"
        path, _ = QFileDialog.getSaveFileName(self, "导出", name, "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data if len(data) > 1 else data[0], f, ensure_ascii=False, indent=2)

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in (data if isinstance(data, list) else [data]):
            b = self._pm.create_build(item.get("name", "导入"))
            self._pm.update_build(b["id"], **{k: v for k, v in item.items() if k in b and k != "id"})
        self._refresh_list()

    def refresh_group_refs(self):
        pass
