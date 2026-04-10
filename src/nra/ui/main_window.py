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
