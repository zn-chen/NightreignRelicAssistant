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

        self._preset_manager = PresetManager(f"{data_dir}/presets.json")
        self._vocab_loader = VocabularyLoader(data_dir)

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

        tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(tabs)
        self._tabs = tabs

    def _on_tab_changed(self, index: int):
        widget = self._tabs.widget(index)
        if widget is self._build_page:
            self._build_page.refresh_group_refs()
