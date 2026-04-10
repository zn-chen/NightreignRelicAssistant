# UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the desktop GUI with build management, common/blacklist group management, settings, and vocabulary loading using PySide6.

**Architecture:** Data layer (VocabularyLoader, PresetManager) is built and tested first, then the reusable AffixEditor widget, then each page, finally wired into MainWindow with QTabWidget.

**Tech Stack:** PySide6, JSON persistence, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/nra/models/vocabulary.py` | Load vocab txt files, search/filter |
| `src/nra/models/preset_manager.py` | CRUD for builds, common groups, blacklist groups; JSON persistence |
| `src/nra/ui/widgets/affix_editor.py` | Reusable search+add affix editor widget |
| `src/nra/ui/pages/home_page.py` | Placeholder home page |
| `src/nra/ui/pages/build_page.py` | Build management page |
| `src/nra/ui/pages/common_page.py` | Common group management page |
| `src/nra/ui/pages/blacklist_page.py` | Blacklist group management page |
| `src/nra/ui/pages/settings_page.py` | Settings page |
| `src/nra/ui/main_window.py` | MainWindow with QTabWidget wiring |
| `tests/test_vocabulary.py` | VocabularyLoader tests |
| `tests/test_preset_manager.py` | PresetManager tests |
| `data/normal.txt` | Normal mode vocab (test data) |
| `data/normal_special.txt` | Normal mode special vocab (test data) |
| `data/deepnight_pos.txt` | Deepnight positive vocab (test data) |
| `data/deepnight_neg.txt` | Deepnight negative vocab (test data) |

---

### Task 1: Test Data — Vocabulary Files

**Files:**
- Create: `data/normal.txt`
- Create: `data/normal_special.txt`
- Create: `data/deepnight_pos.txt`
- Create: `data/deepnight_neg.txt`

- [ ] **Step 1: Create vocabulary test data files**

Create small representative subsets of the game's vocab data for development and testing.

`data/normal.txt`:
```
生命力+1
生命力+2
生命力+3
集中力+1
集中力+2
集中力+3
耐力+1
耐力+2
耐力+3
力气+1
力气+2
力气+3
灵巧+1
灵巧+2
灵巧+3
智力+1
智力+2
智力+3
信仰+1
信仰+2
信仰+3
感应+1
感应+2
感应+3
强韧度+1
强韧度+2
强韧度+3
提升物理攻击力
提升物理攻击力+1
提升物理攻击力+2
提升魔力属性攻击力
提升火属性攻击力
提升雷属性攻击力
提升圣属性攻击力
```

`data/normal_special.txt`:
```
提升血量上限
提升专注值上限
提升精力上限
减少专注值消耗
强化魔法
强化祷告
提升圣杯瓶恢复量
```

`data/deepnight_pos.txt`:
```
提升物理攻击力+3
提升物理攻击力+4
提升魔力属性攻击力+3
提升火属性攻击力+3
提升雷属性攻击力+3
提升圣属性攻击力+3
提升血量上限
提升专注值上限
提升精力上限
提升近战攻击力
提升战技攻击力
连续攻击时，提升攻击力
```

`data/deepnight_neg.txt`:
```
受到损伤时，会累积中毒量表
受到损伤时，会累积出血量表
降低力气、智力
降低灵巧、信仰
降低物理减伤率
持续减少血量
降低圣杯瓶恢复量
```

- [ ] **Step 2: Commit**

```bash
git add data/
git commit -m "data: add vocabulary test data files"
```

---

### Task 2: VocabularyLoader

**Files:**
- Create: `src/nra/models/__init__.py`
- Create: `src/nra/models/vocabulary.py`
- Create: `tests/test_vocabulary.py`

- [ ] **Step 1: Write failing tests**

`tests/test_vocabulary.py`:
```python
import os
import pytest
from nra.models.vocabulary import VocabularyLoader


@pytest.fixture
def data_dir():
    return os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture
def loader(data_dir):
    return VocabularyLoader(data_dir)


def test_load_single_file(loader):
    vocabs = loader.load(["normal.txt"])
    assert len(vocabs) > 0
    assert "生命力+1" in vocabs


def test_load_multiple_files(loader):
    vocabs = loader.load(["normal.txt", "normal_special.txt"])
    assert "生命力+1" in vocabs
    assert "提升血量上限" in vocabs


def test_load_nonexistent_file(loader):
    vocabs = loader.load(["nonexistent.txt"])
    assert vocabs == []


def test_load_deduplicates(loader):
    vocabs = loader.load(["normal.txt", "normal.txt"])
    count = vocabs.count("生命力+1")
    assert count == 1


def test_load_arrow_format(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("1→提升攻击力\n2→提升防御力\n", encoding="utf-8")
    loader = VocabularyLoader(str(tmp_path))
    vocabs = loader.load(["test.txt"])
    assert vocabs == ["提升攻击力", "提升防御力"]


def test_search_exact(loader):
    vocabs = loader.load(["normal.txt"])
    results = loader.search("生命力+1", vocabs)
    assert "生命力+1" in results


def test_search_partial(loader):
    vocabs = loader.load(["normal.txt"])
    results = loader.search("生命", vocabs)
    assert all("生命" in r for r in results)


def test_search_empty_query(loader):
    vocabs = loader.load(["normal.txt"])
    results = loader.search("", vocabs)
    assert results == vocabs


def test_search_no_match(loader):
    vocabs = loader.load(["normal.txt"])
    results = loader.search("不存在的词条xyz", vocabs)
    assert results == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant && python -m pytest tests/test_vocabulary.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nra.models'`

- [ ] **Step 3: Write implementation**

`src/nra/models/__init__.py`:
```python
"""数据模型"""
```

`src/nra/models/vocabulary.py`:
```python
"""词条库加载与搜索"""

import os


class VocabularyLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load(self, files: list[str]) -> list[str]:
        """加载指定文件的词条，去重保序"""
        seen = set()
        vocabs = []
        for filename in files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                continue
            with open(filepath, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if "→" in line:
                        line = line.split("→", 1)[1].strip()
                    if line and line not in seen:
                        seen.add(line)
                        vocabs.append(line)
        return vocabs

    def search(self, query: str, vocabulary: list[str]) -> list[str]:
        """搜索词条，空查询返回全部，否则按包含关系过滤"""
        if not query:
            return vocabulary
        return [v for v in vocabulary if query in v]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant && python -m pytest tests/test_vocabulary.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/nra/models/ tests/test_vocabulary.py
git commit -m "feat: add VocabularyLoader with load and search"
```

---

### Task 3: PresetManager

**Files:**
- Create: `src/nra/models/preset_manager.py`
- Create: `tests/test_preset_manager.py`

- [ ] **Step 1: Write failing tests**

`tests/test_preset_manager.py`:
```python
import os
import json
import pytest
from nra.models.preset_manager import PresetManager


@pytest.fixture
def pm(tmp_path):
    return PresetManager(str(tmp_path / "presets.json"))


def test_initial_state(pm):
    assert pm.builds == []
    assert pm.common_groups == []
    assert pm.blacklist_groups == []


def test_save_and_load(pm):
    pm.create_build("测试Build")
    pm.save()

    pm2 = PresetManager(pm.filepath)
    assert len(pm2.builds) == 1
    assert pm2.builds[0]["name"] == "测试Build"


# --- Build CRUD ---

def test_create_build(pm):
    build = pm.create_build("火法师")
    assert build["name"] == "火法师"
    assert build["id"]
    assert build["include_common"] is True
    assert build["min_matches"] == 2
    assert build["normal_whitelist"] == []
    assert build["deepnight_whitelist"] == []
    assert build["common_group_ids"] == []
    assert build["blacklist_group_ids"] == []


def test_update_build(pm):
    build = pm.create_build("火法师")
    pm.update_build(build["id"], name="冰法师", min_matches=3)
    updated = pm.get_build(build["id"])
    assert updated["name"] == "冰法师"
    assert updated["min_matches"] == 3


def test_delete_build(pm):
    build = pm.create_build("火法师")
    pm.delete_build(build["id"])
    assert len(pm.builds) == 0


def test_update_build_whitelist(pm):
    build = pm.create_build("火法师")
    pm.update_build(build["id"], normal_whitelist=["生命力+3", "智力+3"])
    updated = pm.get_build(build["id"])
    assert updated["normal_whitelist"] == ["生命力+3", "智力+3"]


# --- Common Group CRUD ---

def test_create_common_group(pm):
    group = pm.create_common_group("属性通用")
    assert group["name"] == "属性通用"
    assert group["id"]
    assert group["normal_affixes"] == []
    assert group["deepnight_affixes"] == []


def test_update_common_group(pm):
    group = pm.create_common_group("属性通用")
    pm.update_common_group(group["id"], normal_affixes=["生命力+3"])
    updated = pm.get_common_group(group["id"])
    assert updated["normal_affixes"] == ["生命力+3"]


def test_delete_common_group_cleans_build_refs(pm):
    group = pm.create_common_group("属性通用")
    build = pm.create_build("火法师")
    pm.update_build(build["id"], common_group_ids=[group["id"]])
    pm.delete_common_group(group["id"])
    updated_build = pm.get_build(build["id"])
    assert group["id"] not in updated_build["common_group_ids"]


# --- Blacklist Group CRUD ---

def test_create_blacklist_group(pm):
    group = pm.create_blacklist_group("致命负面")
    assert group["name"] == "致命负面"
    assert group["affixes"] == []


def test_update_blacklist_group(pm):
    group = pm.create_blacklist_group("致命负面")
    pm.update_blacklist_group(group["id"], affixes=["持续减少血量"])
    updated = pm.get_blacklist_group(group["id"])
    assert updated["affixes"] == ["持续减少血量"]


def test_delete_blacklist_group_cleans_build_refs(pm):
    group = pm.create_blacklist_group("致命负面")
    build = pm.create_build("火法师")
    pm.update_build(build["id"], blacklist_group_ids=[group["id"]])
    pm.delete_blacklist_group(group["id"])
    updated_build = pm.get_build(build["id"])
    assert group["id"] not in updated_build["blacklist_group_ids"]


def test_auto_save(pm):
    pm.create_build("自动保存测试")
    pm2 = PresetManager(pm.filepath)
    assert len(pm2.builds) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant && python -m pytest tests/test_preset_manager.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

`src/nra/models/preset_manager.py`:
```python
"""预设管理器 — Build / 通用组 / 黑名单组的 CRUD 与持久化"""

import json
import os
import uuid


class PresetManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.builds: list[dict] = []
        self.common_groups: list[dict] = []
        self.blacklist_groups: list[dict] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.builds = data.get("builds", [])
        self.common_groups = data.get("common_groups", [])
        self.blacklist_groups = data.get("blacklist_groups", [])

    def save(self):
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        data = {
            "version": "1.0",
            "builds": self.builds,
            "common_groups": self.common_groups,
            "blacklist_groups": self.blacklist_groups,
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- Build ---

    def create_build(self, name: str) -> dict:
        build = {
            "id": str(uuid.uuid4()),
            "name": name,
            "include_common": True,
            "common_group_ids": [],
            "blacklist_group_ids": [],
            "min_matches": 2,
            "normal_whitelist": [],
            "deepnight_whitelist": [],
        }
        self.builds.append(build)
        self.save()
        return build

    def get_build(self, build_id: str) -> dict | None:
        for b in self.builds:
            if b["id"] == build_id:
                return b
        return None

    def update_build(self, build_id: str, **kwargs):
        build = self.get_build(build_id)
        if build is None:
            return
        for key, value in kwargs.items():
            if key in build:
                build[key] = value
        self.save()

    def delete_build(self, build_id: str):
        self.builds = [b for b in self.builds if b["id"] != build_id]
        self.save()

    # --- Common Group ---

    def create_common_group(self, name: str) -> dict:
        group = {
            "id": str(uuid.uuid4()),
            "name": name,
            "normal_affixes": [],
            "deepnight_affixes": [],
        }
        self.common_groups.append(group)
        self.save()
        return group

    def get_common_group(self, group_id: str) -> dict | None:
        for g in self.common_groups:
            if g["id"] == group_id:
                return g
        return None

    def update_common_group(self, group_id: str, **kwargs):
        group = self.get_common_group(group_id)
        if group is None:
            return
        for key, value in kwargs.items():
            if key in group:
                group[key] = value
        self.save()

    def delete_common_group(self, group_id: str):
        self.common_groups = [g for g in self.common_groups if g["id"] != group_id]
        for build in self.builds:
            if group_id in build["common_group_ids"]:
                build["common_group_ids"].remove(group_id)
        self.save()

    # --- Blacklist Group ---

    def create_blacklist_group(self, name: str) -> dict:
        group = {
            "id": str(uuid.uuid4()),
            "name": name,
            "affixes": [],
        }
        self.blacklist_groups.append(group)
        self.save()
        return group

    def get_blacklist_group(self, group_id: str) -> dict | None:
        for g in self.blacklist_groups:
            if g["id"] == group_id:
                return g
        return None

    def update_blacklist_group(self, group_id: str, **kwargs):
        group = self.get_blacklist_group(group_id)
        if group is None:
            return
        for key, value in kwargs.items():
            if key in group:
                group[key] = value
        self.save()

    def delete_blacklist_group(self, group_id: str):
        self.blacklist_groups = [g for g in self.blacklist_groups if g["id"] != group_id]
        for build in self.builds:
            if group_id in build["blacklist_group_ids"]:
                build["blacklist_group_ids"].remove(group_id)
        self.save()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant && python -m pytest tests/test_preset_manager.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/nra/models/preset_manager.py tests/test_preset_manager.py
git commit -m "feat: add PresetManager with build/common/blacklist CRUD"
```

---

### Task 4: AffixEditor Widget

**Files:**
- Create: `src/nra/ui/widgets/__init__.py`
- Create: `src/nra/ui/widgets/affix_editor.py`

- [ ] **Step 1: Write the widget**

`src/nra/ui/widgets/__init__.py`:
```python
"""UI 组件"""
```

`src/nra/ui/widgets/affix_editor.py`:
```python
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
```

- [ ] **Step 2: Smoke test manually**

Run:
```bash
cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant
python -c "
import sys
from PySide6.QtWidgets import QApplication
from nra.ui.widgets.affix_editor import AffixEditor
app = QApplication(sys.argv)
w = AffixEditor(['生命力+1', '生命力+2', '智力+1', '智力+2'])
w.show()
app.exec()
"
```

Expected: A window with search box, vocab list, and selected list. Double-click items to add.

- [ ] **Step 3: Commit**

```bash
git add src/nra/ui/widgets/
git commit -m "feat: add AffixEditor reusable widget"
```

---

### Task 5: HomePage

**Files:**
- Create: `src/nra/ui/pages/__init__.py`
- Create: `src/nra/ui/pages/home_page.py`

- [ ] **Step 1: Write the page**

`src/nra/ui/pages/__init__.py`:
```python
"""页面"""
```

`src/nra/ui/pages/home_page.py`:
```python
"""主页 — 占位页面"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("黑夜君临遗物助手")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("v0.1.0")
        version.setStyleSheet("font-size: 14pt; color: gray;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        desc = QLabel("Elden Ring Nightreign 遗物自动化管理工具")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/
git commit -m "feat: add HomePage placeholder"
```

---

### Task 6: CommonPage

**Files:**
- Create: `src/nra/ui/pages/common_page.py`

- [ ] **Step 1: Write the page**

`src/nra/ui/pages/common_page.py`:
```python
"""通用词条组管理页面"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QPushButton, QLineEdit, QTabWidget,
    QLabel, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor


class CommonPage(QWidget):
    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        super().__init__(parent)
        self._pm = preset_manager
        self._vocab = vocab_loader
        self._current_group_id: str | None = None
        self._init_ui()
        self._refresh_group_list()

    def _init_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # 左侧: 组列表
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("通用词条组"))
        self._group_list = QListWidget()
        self._group_list.currentRowChanged.connect(self._on_group_selected)
        left_layout.addWidget(self._group_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新建")
        add_btn.clicked.connect(self._on_add_group)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete_group)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left)

        # 右侧: 编辑区
        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_layout.setContentsMargins(0, 0, 0, 0)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("组名称")
        self._name_input.editingFinished.connect(self._on_name_changed)
        self._right_layout.addWidget(self._name_input)

        # 普通/深夜 tab
        tabs = QTabWidget()
        normal_vocab = self._vocab.load(["normal.txt", "normal_special.txt"])
        self._normal_editor = AffixEditor(normal_vocab)
        self._normal_editor.affixes_changed.connect(self._on_normal_affixes_changed)
        tabs.addTab(self._normal_editor, "普通词条")

        deepnight_vocab = self._vocab.load(["deepnight_pos.txt"])
        self._deepnight_editor = AffixEditor(deepnight_vocab)
        self._deepnight_editor.affixes_changed.connect(self._on_deepnight_affixes_changed)
        tabs.addTab(self._deepnight_editor, "深夜词条")

        self._right_layout.addWidget(tabs)
        self._right_panel.setEnabled(False)

        splitter.addWidget(self._right_panel)
        splitter.setSizes([200, 600])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def _refresh_group_list(self):
        self._group_list.clear()
        for group in self._pm.common_groups:
            self._group_list.addItem(group["name"])

    def _on_group_selected(self, row: int):
        if row < 0 or row >= len(self._pm.common_groups):
            self._current_group_id = None
            self._right_panel.setEnabled(False)
            return
        group = self._pm.common_groups[row]
        self._current_group_id = group["id"]
        self._right_panel.setEnabled(True)
        self._name_input.setText(group["name"])
        self._normal_editor.set_affixes(group["normal_affixes"])
        self._deepnight_editor.set_affixes(group["deepnight_affixes"])

    def _on_add_group(self):
        name, ok = QInputDialog.getText(self, "新建通用组", "组名称:")
        if ok and name.strip():
            self._pm.create_common_group(name.strip())
            self._refresh_group_list()
            self._group_list.setCurrentRow(len(self._pm.common_groups) - 1)

    def _on_delete_group(self):
        if self._current_group_id is None:
            return
        reply = QMessageBox.question(self, "确认删除", "删除该通用组？引用此组的 build 将自动解除关联。")
        if reply == QMessageBox.Yes:
            self._pm.delete_common_group(self._current_group_id)
            self._current_group_id = None
            self._refresh_group_list()

    def _on_name_changed(self):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, name=self._name_input.text())
            row = self._group_list.currentRow()
            self._refresh_group_list()
            self._group_list.setCurrentRow(row)

    def _on_normal_affixes_changed(self, affixes: list):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, normal_affixes=affixes)

    def _on_deepnight_affixes_changed(self, affixes: list):
        if self._current_group_id:
            self._pm.update_common_group(self._current_group_id, deepnight_affixes=affixes)
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/common_page.py
git commit -m "feat: add CommonPage for common affix group management"
```

---

### Task 7: BlacklistPage

**Files:**
- Create: `src/nra/ui/pages/blacklist_page.py`

- [ ] **Step 1: Write the page**

`src/nra/ui/pages/blacklist_page.py`:
```python
"""黑名单组管理页面"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QPushButton, QLineEdit, QLabel,
    QInputDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor


class BlacklistPage(QWidget):
    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        super().__init__(parent)
        self._pm = preset_manager
        self._vocab = vocab_loader
        self._current_group_id: str | None = None
        self._init_ui()
        self._refresh_group_list()

    def _init_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # 左侧: 组列表
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("黑名单组"))
        self._group_list = QListWidget()
        self._group_list.currentRowChanged.connect(self._on_group_selected)
        left_layout.addWidget(self._group_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新建")
        add_btn.clicked.connect(self._on_add_group)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete_group)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left)

        # 右侧: 编辑区
        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_layout.setContentsMargins(0, 0, 0, 0)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("组名称")
        self._name_input.editingFinished.connect(self._on_name_changed)
        self._right_layout.addWidget(self._name_input)

        neg_vocab = self._vocab.load(["deepnight_neg.txt"])
        self._affix_editor = AffixEditor(neg_vocab)
        self._affix_editor.affixes_changed.connect(self._on_affixes_changed)
        self._right_layout.addWidget(self._affix_editor)

        self._right_panel.setEnabled(False)
        splitter.addWidget(self._right_panel)
        splitter.setSizes([200, 600])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def _refresh_group_list(self):
        self._group_list.clear()
        for group in self._pm.blacklist_groups:
            self._group_list.addItem(group["name"])

    def _on_group_selected(self, row: int):
        if row < 0 or row >= len(self._pm.blacklist_groups):
            self._current_group_id = None
            self._right_panel.setEnabled(False)
            return
        group = self._pm.blacklist_groups[row]
        self._current_group_id = group["id"]
        self._right_panel.setEnabled(True)
        self._name_input.setText(group["name"])
        self._affix_editor.set_affixes(group["affixes"])

    def _on_add_group(self):
        name, ok = QInputDialog.getText(self, "新建黑名单组", "组名称:")
        if ok and name.strip():
            self._pm.create_blacklist_group(name.strip())
            self._refresh_group_list()
            self._group_list.setCurrentRow(len(self._pm.blacklist_groups) - 1)

    def _on_delete_group(self):
        if self._current_group_id is None:
            return
        reply = QMessageBox.question(self, "确认删除", "删除该黑名单组？引用此组的 build 将自动解除关联。")
        if reply == QMessageBox.Yes:
            self._pm.delete_blacklist_group(self._current_group_id)
            self._current_group_id = None
            self._refresh_group_list()

    def _on_name_changed(self):
        if self._current_group_id:
            self._pm.update_blacklist_group(self._current_group_id, name=self._name_input.text())
            row = self._group_list.currentRow()
            self._refresh_group_list()
            self._group_list.setCurrentRow(row)

    def _on_affixes_changed(self, affixes: list):
        if self._current_group_id:
            self._pm.update_blacklist_group(self._current_group_id, affixes=affixes)
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/blacklist_page.py
git commit -m "feat: add BlacklistPage for blacklist group management"
```

---

### Task 8: BuildPage

**Files:**
- Create: `src/nra/ui/pages/build_page.py`

- [ ] **Step 1: Write the page**

`src/nra/ui/pages/build_page.py`:
```python
"""Build 管理页面"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QPushButton, QLineEdit, QTabWidget,
    QLabel, QCheckBox, QSpinBox, QInputDialog,
    QMessageBox, QGroupBox, QScrollArea,
)
from PySide6.QtCore import Qt
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.widgets.affix_editor import AffixEditor


class BuildPage(QWidget):
    def __init__(self, preset_manager: PresetManager, vocab_loader: VocabularyLoader, parent=None):
        super().__init__(parent)
        self._pm = preset_manager
        self._vocab = vocab_loader
        self._current_build_id: str | None = None
        self._init_ui()
        self._refresh_build_list()

    def _init_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # 左侧: build 列表
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("角色 Build"))
        self._build_list = QListWidget()
        self._build_list.currentRowChanged.connect(self._on_build_selected)
        left_layout.addWidget(self._build_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新建")
        add_btn.clicked.connect(self._on_add_build)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete_build)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left)

        # 右侧: 编辑区 (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)

        # 名称
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Build 名称")
        self._name_input.editingFinished.connect(self._on_name_changed)
        self._right_layout.addWidget(self._name_input)

        # 匹配数
        match_layout = QHBoxLayout()
        match_layout.addWidget(QLabel("最少命中词条数:"))
        self._min_matches = QSpinBox()
        self._min_matches.setRange(1, 6)
        self._min_matches.setValue(2)
        self._min_matches.valueChanged.connect(self._on_min_matches_changed)
        match_layout.addWidget(self._min_matches)
        match_layout.addStretch()
        self._right_layout.addLayout(match_layout)

        # 通用组引用
        common_group = QGroupBox("引用通用词条组")
        common_group.setCheckable(True)
        common_group.setChecked(True)
        common_group.toggled.connect(self._on_include_common_changed)
        self._common_group_box = common_group
        common_layout = QVBoxLayout(common_group)
        self._common_checks: list[tuple[QCheckBox, str]] = []
        self._common_checks_layout = QVBoxLayout()
        common_layout.addLayout(self._common_checks_layout)
        self._right_layout.addWidget(common_group)

        # 黑名单引用
        blacklist_group = QGroupBox("引用黑名单组")
        blacklist_layout = QVBoxLayout(blacklist_group)
        self._blacklist_checks: list[tuple[QCheckBox, str]] = []
        self._blacklist_checks_layout = QVBoxLayout()
        blacklist_layout.addLayout(self._blacklist_checks_layout)
        self._right_layout.addWidget(blacklist_group)

        # 白名单编辑
        tabs = QTabWidget()
        normal_vocab = self._vocab.load(["normal.txt", "normal_special.txt"])
        self._normal_editor = AffixEditor(normal_vocab)
        self._normal_editor.affixes_changed.connect(self._on_normal_wl_changed)
        tabs.addTab(self._normal_editor, "普通白名单")

        deepnight_vocab = self._vocab.load(["deepnight_pos.txt"])
        self._deepnight_editor = AffixEditor(deepnight_vocab)
        self._deepnight_editor.affixes_changed.connect(self._on_deepnight_wl_changed)
        tabs.addTab(self._deepnight_editor, "深夜白名单")

        self._right_layout.addWidget(tabs)
        self._right_panel.setEnabled(False)

        scroll.setWidget(self._right_panel)
        splitter.addWidget(scroll)
        splitter.setSizes([200, 600])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def _refresh_build_list(self):
        self._build_list.clear()
        for build in self._pm.builds:
            self._build_list.addItem(build["name"])

    def _refresh_group_checkboxes(self):
        # 清空通用组 checkboxes
        for cb, _ in self._common_checks:
            self._common_checks_layout.removeWidget(cb)
            cb.deleteLater()
        self._common_checks.clear()

        build = self._pm.get_build(self._current_build_id) if self._current_build_id else None

        for group in self._pm.common_groups:
            cb = QCheckBox(group["name"])
            if build:
                cb.setChecked(group["id"] in build["common_group_ids"])
            cb.stateChanged.connect(self._on_common_group_toggled)
            self._common_checks.append((cb, group["id"]))
            self._common_checks_layout.addWidget(cb)

        # 清空黑名单 checkboxes
        for cb, _ in self._blacklist_checks:
            self._blacklist_checks_layout.removeWidget(cb)
            cb.deleteLater()
        self._blacklist_checks.clear()

        for group in self._pm.blacklist_groups:
            cb = QCheckBox(group["name"])
            if build:
                cb.setChecked(group["id"] in build["blacklist_group_ids"])
            cb.stateChanged.connect(self._on_blacklist_group_toggled)
            self._blacklist_checks.append((cb, group["id"]))
            self._blacklist_checks_layout.addWidget(cb)

    def _on_build_selected(self, row: int):
        if row < 0 or row >= len(self._pm.builds):
            self._current_build_id = None
            self._right_panel.setEnabled(False)
            return
        build = self._pm.builds[row]
        self._current_build_id = build["id"]
        self._right_panel.setEnabled(True)
        self._name_input.setText(build["name"])
        self._min_matches.setValue(build["min_matches"])
        self._common_group_box.setChecked(build["include_common"])
        self._normal_editor.set_affixes(build["normal_whitelist"])
        self._deepnight_editor.set_affixes(build["deepnight_whitelist"])
        self._refresh_group_checkboxes()

    def _on_add_build(self):
        name, ok = QInputDialog.getText(self, "新建 Build", "Build 名称:")
        if ok and name.strip():
            self._pm.create_build(name.strip())
            self._refresh_build_list()
            self._build_list.setCurrentRow(len(self._pm.builds) - 1)

    def _on_delete_build(self):
        if self._current_build_id is None:
            return
        reply = QMessageBox.question(self, "确认删除", "删除该 Build？")
        if reply == QMessageBox.Yes:
            self._pm.delete_build(self._current_build_id)
            self._current_build_id = None
            self._refresh_build_list()

    def _on_name_changed(self):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, name=self._name_input.text())
            row = self._build_list.currentRow()
            self._refresh_build_list()
            self._build_list.setCurrentRow(row)

    def _on_min_matches_changed(self, value: int):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, min_matches=value)

    def _on_include_common_changed(self, checked: bool):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, include_common=checked)

    def _on_common_group_toggled(self):
        if not self._current_build_id:
            return
        ids = [gid for cb, gid in self._common_checks if cb.isChecked()]
        self._pm.update_build(self._current_build_id, common_group_ids=ids)

    def _on_blacklist_group_toggled(self):
        if not self._current_build_id:
            return
        ids = [gid for cb, gid in self._blacklist_checks if cb.isChecked()]
        self._pm.update_build(self._current_build_id, blacklist_group_ids=ids)

    def _on_normal_wl_changed(self, affixes: list):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, normal_whitelist=affixes)

    def _on_deepnight_wl_changed(self, affixes: list):
        if self._current_build_id:
            self._pm.update_build(self._current_build_id, deepnight_whitelist=affixes)

    def refresh_group_refs(self):
        """外部调用：通用/黑名单组变化后刷新 checkboxes"""
        if self._current_build_id:
            self._refresh_group_checkboxes()
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/build_page.py
git commit -m "feat: add BuildPage with whitelist editing and group references"
```

---

### Task 9: SettingsPage

**Files:**
- Create: `src/nra/ui/pages/settings_page.py`

- [ ] **Step 1: Write the page**

`src/nra/ui/pages/settings_page.py`:
```python
"""设置页面"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QGroupBox,
)


class SettingsPage(QWidget):
    def __init__(self, settings_path: str, parent=None):
        super().__init__(parent)
        self._settings_path = settings_path
        self._settings = self._load()
        self._init_ui()

    def _load(self) -> dict:
        if os.path.exists(self._settings_path):
            with open(self._settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"vocab_dir": "data", "data_dir": "data"}

    def _save(self):
        os.makedirs(os.path.dirname(self._settings_path) or ".", exist_ok=True)
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 路径配置
        paths_group = QGroupBox("路径配置")
        paths_layout = QVBoxLayout(paths_group)

        # 词条库路径
        vocab_layout = QHBoxLayout()
        vocab_layout.addWidget(QLabel("词条库目录:"))
        self._vocab_dir_input = QLineEdit(self._settings.get("vocab_dir", "data"))
        self._vocab_dir_input.editingFinished.connect(self._on_vocab_dir_changed)
        vocab_layout.addWidget(self._vocab_dir_input)
        vocab_browse = QPushButton("浏览")
        vocab_browse.clicked.connect(self._browse_vocab_dir)
        vocab_layout.addWidget(vocab_browse)
        paths_layout.addLayout(vocab_layout)

        # 数据存储路径
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("数据存储目录:"))
        self._data_dir_input = QLineEdit(self._settings.get("data_dir", "data"))
        self._data_dir_input.editingFinished.connect(self._on_data_dir_changed)
        data_layout.addWidget(self._data_dir_input)
        data_browse = QPushButton("浏览")
        data_browse.clicked.connect(self._browse_data_dir)
        data_layout.addWidget(data_browse)
        paths_layout.addLayout(data_layout)

        layout.addWidget(paths_group)
        layout.addStretch()

    def _browse_vocab_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择词条库目录")
        if d:
            self._vocab_dir_input.setText(d)
            self._on_vocab_dir_changed()

    def _browse_data_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择数据存储目录")
        if d:
            self._data_dir_input.setText(d)
            self._on_data_dir_changed()

    def _on_vocab_dir_changed(self):
        self._settings["vocab_dir"] = self._vocab_dir_input.text()
        self._save()

    def _on_data_dir_changed(self):
        self._settings["data_dir"] = self._data_dir_input.text()
        self._save()
```

- [ ] **Step 2: Commit**

```bash
git add src/nra/ui/pages/settings_page.py
git commit -m "feat: add SettingsPage with path configuration"
```

---

### Task 10: Wire MainWindow

**Files:**
- Modify: `src/nra/ui/main_window.py`
- Modify: `src/nra/main.py`

- [ ] **Step 1: Update MainWindow**

Replace `src/nra/ui/main_window.py` with:
```python
"""主窗口"""

from PySide6.QtWidgets import QMainWindow, QTabWidget
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.pages.home_page import HomePage
from nra.ui.pages.build_page import BuildPage
from nra.ui.pages.common_page import CommonPage
from nra.ui.pages.blacklist_page import BlacklistPage
from nra.ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, data_dir: str = "data"):
        super().__init__()
        self.setWindowTitle("黑夜君临遗物助手 v0.1.0")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # 数据层
        self._preset_manager = PresetManager(f"{data_dir}/presets.json")
        self._vocab_loader = VocabularyLoader(data_dir)

        # 标签页
        tabs = QTabWidget()

        self._home_page = HomePage()
        tabs.addTab(self._home_page, "主页")

        self._build_page = BuildPage(self._preset_manager, self._vocab_loader)
        tabs.addTab(self._build_page, "Build 管理")

        self._common_page = CommonPage(self._preset_manager, self._vocab_loader)
        tabs.addTab(self._common_page, "通用管理")

        self._blacklist_page = BlacklistPage(self._preset_manager, self._vocab_loader)
        tabs.addTab(self._blacklist_page, "黑名单管理")

        self._settings_page = SettingsPage(f"{data_dir}/settings.json")
        tabs.addTab(self._settings_page, "设置")

        # 切换到 Build 页面时刷新组引用（通用/黑名单可能已变化）
        tabs.currentChanged.connect(self._on_tab_changed)

        self.setCentralWidget(tabs)
        self._tabs = tabs

    def _on_tab_changed(self, index: int):
        widget = self._tabs.widget(index)
        if widget is self._build_page:
            self._build_page.refresh_group_refs()
```

- [ ] **Step 2: Update main.py**

Replace `src/nra/main.py` with:
```python
"""程序入口"""

import sys
import os


def main():
    from PySide6.QtWidgets import QApplication
    from nra.ui.main_window import MainWindow

    app = QApplication(sys.argv)

    # 数据目录: 优先使用可执行文件同级的 data/，否则用项目根的 data/
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    data_dir = os.path.normpath(data_dir)

    window = MainWindow(data_dir=data_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the app**

```bash
cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant
pip install -e .
python -m nra.main
```

Expected: Window with 5 tabs. Build/通用/黑名单页面可以创建/编辑/删除。词条搜索和添加功能正常。

- [ ] **Step 4: Run all tests**

```bash
cd /Users/czn/Projects/github.com/czn/NightreignRelicAssistant
python -m pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/nra/ui/main_window.py src/nra/main.py
git commit -m "feat: wire MainWindow with all pages and data layer"
```
