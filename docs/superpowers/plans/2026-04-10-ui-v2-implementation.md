# UI v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement PySide6 native UI with button nav bar, 4 pages, affix editor widget, following all constraints from the v2 spec.

**Architecture:** Fusion style, button-based navigation + QStackedWidget, QFrame cards for visual grouping, no custom theming.

**Tech Stack:** PySide6 (native only, no third-party UI libs)

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/nra/main.py` | Entry point, QApplication + Fusion style |
| `src/nra/ui/widgets/cards.py` | make_card helper |
| `src/nra/ui/widgets/affix_editor.py` | Reusable search+add affix editor |
| `src/nra/ui/pages/shop_page.py` | 自动购买 |
| `src/nra/ui/pages/repo_page.py` | 仓库整理 |
| `src/nra/ui/pages/build_page.py` | 构筑管理 |
| `src/nra/ui/pages/settings_page.py` | 设置 |
| `src/nra/ui/main_window.py` | MainWindow + nav bar + QStackedWidget |

---

### Task 1: Entry Point + Cards Helper

**Files:**
- Modify: `src/nra/main.py`
- Create: `src/nra/ui/widgets/__init__.py`
- Create: `src/nra/ui/widgets/cards.py`

- [ ] **Step 1: Write main.py**

```python
"""程序入口"""

import sys
import os


def main():
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from nra.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    data_dir = os.path.normpath(data_dir)

    window = MainWindow(data_dir=data_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write cards.py**

```python
"""卡片容器"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


def make_card(title=None):
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)
    if title:
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
    return frame, layout
```

- [ ] **Step 3: Write widgets/__init__.py**

```python
"""UI 组件"""
```

- [ ] **Step 4: Commit**

```bash
git add src/nra/main.py src/nra/ui/widgets/
git commit -m "feat: entry point with Fusion style + make_card helper"
```

---

### Task 2: AffixEditor Widget

**Files:**
- Create: `src/nra/ui/widgets/affix_editor.py`

- [ ] **Step 1: Write affix_editor.py**

```python
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

        vocab_label = QLabel("词条库")
        vocab_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(vocab_label)

        self._vocab_list = QListWidget()
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
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/widgets/affix_editor.py
git commit -m "feat: add AffixEditor widget"
```

---

### Task 3: ShopPage + RepoPage

**Files:**
- Create: `src/nra/ui/pages/__init__.py`
- Create: `src/nra/ui/pages/shop_page.py`
- Create: `src/nra/ui/pages/repo_page.py`

- [ ] **Step 1: Write pages/__init__.py**

```python
"""页面"""
```

- [ ] **Step 2: Write shop_page.py**

```python
"""自动购买页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTextEdit, QLabel,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.cards import make_card


class ShopPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 左侧
        left = QVBoxLayout()
        left.setSpacing(12)

        match_card, ml = make_card("匹配设置")
        row = QHBoxLayout()
        row.addWidget(QLabel("匹配模式:"))
        self._match = QComboBox()
        self._match.addItems(["双有效", "三有效"])
        row.addWidget(self._match)
        ml.addLayout(row)
        left.addWidget(match_card)

        stop_card, sl = make_card("停止条件")
        self._no_limit = QCheckBox("不限制")
        self._no_limit.setChecked(True)
        self._no_limit.toggled.connect(lambda c: self._threshold.setEnabled(not c))
        sl.addWidget(self._no_limit)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("暗痕阈值:"))
        self._threshold = QSpinBox()
        self._threshold.setRange(0, 999999)
        self._threshold.setValue(10000)
        self._threshold.setSingleStep(1000)
        self._threshold.setEnabled(False)
        row2.addWidget(self._threshold)
        sl.addLayout(row2)
        left.addWidget(stop_card)

        btns = QHBoxLayout()
        self._start = QPushButton("开始")
        self._start.setMinimumHeight(36)
        self._stop = QPushButton("停止")
        self._stop.setMinimumHeight(36)
        self._stop.setEnabled(False)
        btns.addWidget(self._start)
        btns.addWidget(self._stop)
        left.addLayout(btns)
        left.addStretch()
        layout.addLayout(left, 1)

        # 右侧
        right = QVBoxLayout()
        right.setSpacing(12)

        stats_card, stl = make_card("统计")
        stats_row = QHBoxLayout()
        self._stats = {}
        for name in ["购买", "合格", "不合格", "售出"]:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignCenter)
            num = QLabel("0")
            num.setStyleSheet("font-size: 20px; font-weight: bold;")
            num.setAlignment(Qt.AlignCenter)
            col.addWidget(num)
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            col.addWidget(lbl)
            stats_row.addLayout(col)
            self._stats[name] = num
        stl.addLayout(stats_row)
        right.addWidget(stats_card)

        log_card, ll = make_card("日志")
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        ll.addWidget(self._log)
        right.addWidget(log_card, 1)

        layout.addLayout(right, 2)
```

- [ ] **Step 3: Write repo_page.py**

```python
"""仓库整理页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTextEdit, QLabel,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.cards import make_card


class RepoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 左侧
        left = QVBoxLayout()
        left.setSpacing(12)

        match_card, ml = make_card("匹配设置")
        row = QHBoxLayout()
        row.addWidget(QLabel("匹配模式:"))
        self._match = QComboBox()
        self._match.addItems(["双有效", "三有效"])
        row.addWidget(self._match)
        ml.addLayout(row)
        left.addWidget(match_card)

        count_card, cl = make_card("数量设置")
        self._no_limit = QCheckBox("不限制")
        self._no_limit.setChecked(True)
        self._no_limit.toggled.connect(lambda c: self._max.setEnabled(not c))
        cl.addWidget(self._no_limit)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("最大检测数:"))
        self._max = QSpinBox()
        self._max.setRange(1, 999)
        self._max.setValue(100)
        self._max.setEnabled(False)
        row2.addWidget(self._max)
        cl.addLayout(row2)
        left.addWidget(count_card)

        btns = QHBoxLayout()
        self._start = QPushButton("开始清理")
        self._start.setMinimumHeight(36)
        self._stop = QPushButton("停止")
        self._stop.setMinimumHeight(36)
        self._stop.setEnabled(False)
        btns.addWidget(self._start)
        btns.addWidget(self._stop)
        left.addLayout(btns)
        left.addStretch()
        layout.addLayout(left, 1)

        # 右侧
        right = QVBoxLayout()
        right.setSpacing(12)

        stats_card, stl = make_card("统计")
        stats_row = QHBoxLayout()
        self._stats = {}
        for name in ["检测", "合格", "不合格", "售出"]:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignCenter)
            num = QLabel("0")
            num.setStyleSheet("font-size: 20px; font-weight: bold;")
            num.setAlignment(Qt.AlignCenter)
            col.addWidget(num)
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            col.addWidget(lbl)
            stats_row.addLayout(col)
            self._stats[name] = num
        stl.addLayout(stats_row)
        right.addWidget(stats_card)

        log_card, ll = make_card("日志")
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        ll.addWidget(self._log)
        right.addWidget(log_card, 1)

        layout.addLayout(right, 2)
```

- [ ] **Step 4: Commit**

```bash
git add src/nra/ui/pages/
git commit -m "feat: add ShopPage and RepoPage"
```

---

### Task 4: BuildPage

**Files:**
- Create: `src/nra/ui/pages/build_page.py`

- [ ] **Step 1: Write build_page.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/build_page.py
git commit -m "feat: add BuildPage with affix tabs and import/export"
```

---

### Task 5: SettingsPage

**Files:**
- Create: `src/nra/ui/pages/settings_page.py`

- [ ] **Step 1: Write settings_page.py**

```python
"""设置页面"""

import json
import os
import re
import shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QScrollArea, QInputDialog, QMessageBox, QComboBox,
    QListWidget, QListWidgetItem, QFrame,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.cards import make_card


class SettingsPage(QWidget):
    def __init__(self, settings_path, parent=None):
        super().__init__(parent)
        self._path = settings_path
        self._settings = self._load()
        self._steam_users = {}
        self._steam_id = None
        self._init_ui()
        self._refresh_users()

    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"steam_path": "", "backup_dir": "data/save_backups",
                "dingtalk_enabled": False, "dingtalk_webhook": ""}

    def _save(self):
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(12, 12, 12, 12)
        cl.setSpacing(12)

        # 通知
        nc, nl = make_card("出货通知")
        self._ding_cb = QCheckBox("启用钉钉通知")
        self._ding_cb.setChecked(self._settings.get("dingtalk_enabled", False))
        self._ding_cb.toggled.connect(lambda c: self._set("dingtalk_enabled", c))
        nl.addWidget(self._ding_cb)
        wr = QHBoxLayout()
        wr.addWidget(QLabel("Webhook:"))
        self._webhook = QLineEdit(self._settings.get("dingtalk_webhook", ""))
        self._webhook.setPlaceholderText("钉钉机器人 Webhook 地址")
        self._webhook.editingFinished.connect(lambda: self._set("dingtalk_webhook", self._webhook.text()))
        wr.addWidget(self._webhook)
        nl.addLayout(wr)
        cl.addWidget(nc)

        # Steam
        uc, ul = make_card("Steam 用户")
        sr = QHBoxLayout()
        sr.addWidget(QLabel("Steam 路径:"))
        self._steam = QLineEdit(self._settings.get("steam_path", ""))
        self._steam.setPlaceholderText("留空自动检测")
        self._steam.editingFinished.connect(self._on_steam_changed)
        sr.addWidget(self._steam)
        sb = QPushButton("浏览")
        sb.clicked.connect(lambda: self._browse("steam_path", self._steam, "选择 Steam 目录"))
        sr.addWidget(sb)
        ul.addLayout(sr)
        ur = QHBoxLayout()
        ur.addWidget(QLabel("用户:"))
        self._user_combo = QComboBox()
        self._user_combo.currentIndexChanged.connect(self._on_user_changed)
        ur.addWidget(self._user_combo, 1)
        rb = QPushButton("刷新")
        rb.clicked.connect(self._refresh_users)
        ur.addWidget(rb)
        ul.addLayout(ur)
        cl.addWidget(uc)

        # 存档
        sc, svl = make_card("当前存档")
        self._save_label = QLabel("未检测")
        svl.addWidget(self._save_label)
        br = QHBoxLayout()
        self._bkup_btn = QPushButton("备份当前存档")
        self._bkup_btn.clicked.connect(self._on_backup)
        self._bkup_btn.setEnabled(False)
        br.addWidget(self._bkup_btn)
        br.addStretch()
        svl.addLayout(br)
        cl.addWidget(sc)

        # 备份列表
        bc, bl = make_card("备份列表")
        dr = QHBoxLayout()
        dr.addWidget(QLabel("备份目录:"))
        self._bdir = QLineEdit(self._settings.get("backup_dir", "data/save_backups"))
        self._bdir.editingFinished.connect(lambda: (self._set("backup_dir", self._bdir.text()), self._refresh_backups()))
        dr.addWidget(self._bdir)
        db = QPushButton("浏览")
        db.clicked.connect(lambda: (self._browse("backup_dir", self._bdir, "选择备份目录"), self._refresh_backups()))
        dr.addWidget(db)
        bl.addLayout(dr)
        self._bklist = QListWidget()
        self._bklist.setMinimumHeight(150)
        bl.addWidget(self._bklist)
        bbr = QHBoxLayout()
        for text, handler in [("恢复", self._on_restore), ("重命名", self._on_rename), ("删除", self._on_del_backup)]:
            b = QPushButton(text)
            b.clicked.connect(handler)
            bbr.addWidget(b)
        bbr.addStretch()
        bl.addLayout(bbr)
        cl.addWidget(bc)

        cl.addStretch()
        scroll.setWidget(content)
        page = QVBoxLayout(self)
        page.setContentsMargins(0, 0, 0, 0)
        page.addWidget(scroll)

    def _set(self, key, val):
        self._settings[key] = val
        self._save()

    def _browse(self, key, line_edit, title):
        d = QFileDialog.getExistingDirectory(self, title)
        if d:
            line_edit.setText(d)
            self._set(key, d)

    def _on_steam_changed(self):
        self._set("steam_path", self._steam.text())
        self._refresh_users()

    def _refresh_users(self):
        self._steam_users = {}
        self._user_combo.clear()
        sp = self._settings.get("steam_path", "")
        if not sp:
            for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam",
                       os.path.expanduser("~/Library/Application Support/Steam")]:
                if os.path.isdir(p):
                    sp = p
                    break
        if not sp or not os.path.isdir(sp):
            self._user_combo.addItem("未找到 Steam")
            self._update_save()
            return
        vdf = os.path.join(sp, "config", "loginusers.vdf")
        if not os.path.exists(vdf):
            self._user_combo.addItem("未找到用户配置")
            self._update_save()
            return
        try:
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for uid, block in re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content):
                props = dict(re.findall(r'"(\w+)"\s+"([^"]*)"', block))
                self._steam_users[uid] = props
                name = props.get("PersonaName", uid)
                tag = " [最近]" if props.get("MostRecent") == "1" else ""
                self._user_combo.addItem(f"{name}{tag}", uid)
        except Exception:
            self._user_combo.addItem("解析失败")
        self._update_save()

    def _on_user_changed(self, i):
        self._steam_id = self._user_combo.itemData(i) if i >= 0 else None
        self._update_save()
        self._refresh_backups()

    def _save_path(self):
        if not self._steam_id:
            return ""
        return os.path.join(os.environ.get("APPDATA", ""), "Nightreign", self._steam_id, "NR0000.sl2")

    def _update_save(self):
        p = self._save_path()
        if not p:
            self._save_label.setText("请选择用户")
            self._bkup_btn.setEnabled(False)
        elif os.path.exists(p):
            s = os.path.getsize(p) / 1048576
            t = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
            self._save_label.setText(f"已找到 | {s:.1f} MB | {t}")
            self._bkup_btn.setEnabled(True)
        else:
            self._save_label.setText(f"未找到: {p}")
            self._bkup_btn.setEnabled(False)

    def _backup_dir(self):
        base = self._settings.get("backup_dir", "data/save_backups")
        return os.path.join(base, self._steam_id) if self._steam_id else base

    def _on_backup(self):
        p = self._save_path()
        if not p or not os.path.exists(p):
            return
        name, ok = QInputDialog.getText(self, "备份", "名称:", text=datetime.now().strftime("%Y%m%d_%H%M%S"))
        if not ok or not name.strip():
            return
        d = self._backup_dir()
        os.makedirs(d, exist_ok=True)
        shutil.copy2(p, os.path.join(d, f"{name.strip()}.sl2"))
        self._refresh_backups()

    def _refresh_backups(self):
        self._bklist.clear()
        d = self._backup_dir()
        if not os.path.isdir(d):
            return
        files = [(f, os.path.join(d, f)) for f in os.listdir(d) if f.endswith(".sl2")]
        files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
        for name, fp in files:
            t = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
            s = os.path.getsize(fp) / 1048576
            item = QListWidgetItem(f"{name[:-4]} | {t} | {s:.1f} MB")
            item.setData(Qt.UserRole, fp)
            self._bklist.addItem(item)

    def _on_restore(self):
        item = self._bklist.currentItem()
        if not item:
            return
        p = self._save_path()
        if not p:
            return
        if QMessageBox.question(self, "确认", "恢复前会自动备份。继续？") != QMessageBox.Yes:
            return
        if os.path.exists(p):
            d = self._backup_dir()
            os.makedirs(d, exist_ok=True)
            shutil.copy2(p, os.path.join(d, f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sl2"))
        shutil.copy2(item.data(Qt.UserRole), p)
        self._update_save()
        self._refresh_backups()

    def _on_rename(self):
        item = self._bklist.currentItem()
        if not item:
            return
        old = item.data(Qt.UserRole)
        name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=os.path.basename(old)[:-4])
        if ok and name.strip():
            os.rename(old, os.path.join(os.path.dirname(old), f"{name.strip()}.sl2"))
            self._refresh_backups()

    def _on_del_backup(self):
        item = self._bklist.currentItem()
        if not item:
            return
        if QMessageBox.question(self, "确认", "删除该备份？") == QMessageBox.Yes:
            os.remove(item.data(Qt.UserRole))
            self._refresh_backups()
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/settings_page.py
git commit -m "feat: add SettingsPage with notification and save management"
```

---

### Task 6: MainWindow + Wire Everything

**Files:**
- Create: `src/nra/ui/main_window.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write main_window.py**

```python
"""主窗口"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QButtonGroup,
)
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.pages.shop_page import ShopPage
from nra.ui.pages.repo_page import RepoPage
from nra.ui.pages.build_page import BuildPage
from nra.ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, data_dir="data"):
        super().__init__()
        self.setWindowTitle("黑夜君临遗物助手 v0.1.0")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        pm = PresetManager(f"{data_dir}/presets.json")
        vl = VocabularyLoader(data_dir)

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 导航栏
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(12, 8, 12, 8)
        nav_layout.setSpacing(4)

        self._stack = QStackedWidget()
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        pages = [
            ("自动购买", ShopPage()),
            ("仓库整理", RepoPage()),
            ("构筑管理", BuildPage(pm, vl)),
            ("设置", SettingsPage(f"{data_dir}/settings.json")),
        ]

        for i, (label, page) in enumerate(pages):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setMinimumHeight(32)
            btn.setMinimumWidth(80)
            if i == 0:
                btn.setChecked(True)
            self._nav_group.addButton(btn, i)
            nav_layout.addWidget(btn)
            self._stack.addWidget(page)

        nav_layout.addStretch()
        self._nav_group.idClicked.connect(self._stack.setCurrentIndex)

        root.addWidget(nav)
        root.addWidget(self._stack, 1)

        self.setCentralWidget(central)
```

- [ ] **Step 2: Update pyproject.toml dependencies**

```toml
dependencies = [
    "PySide6>=6.5.0",
]
```

- [ ] **Step 3: Run all tests**

```bash
cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant
python3 -m pytest tests/ -v
```

Expected: All 35 PASS

- [ ] **Step 4: Run the app**

```bash
venv/bin/pip install -e .
venv/bin/python -m nra.main
```

Expected: Window with nav bar + 4 pages working

- [ ] **Step 5: Commit**

```bash
git add src/nra/ui/main_window.py pyproject.toml
git commit -m "feat: wire MainWindow with nav bar and all pages"
```
