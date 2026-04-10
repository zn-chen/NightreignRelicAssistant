"""主窗口"""

from PySide6.QtWidgets import QMainWindow, QTabWidget, QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from nra.models.preset_manager import PresetManager
from nra.models.vocabulary import VocabularyLoader
from nra.ui.pages.shop_page import ShopPage
from nra.ui.pages.repo_page import RepoPage
from nra.ui.pages.build_page import BuildPage
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

        self._shop_page = ShopPage()
        tabs.addTab(self._shop_page, "自动购买")

        self._repo_page = RepoPage()
        tabs.addTab(self._repo_page, "仓库整理")

        self._build_page = BuildPage(self._preset_manager, self._vocab_loader)
        tabs.addTab(self._build_page, "构筑管理")

        self._settings_page = SettingsPage(f"{data_dir}/settings.json")
        tabs.addTab(self._settings_page, "设置")

        self._settings_page.theme_changed.connect(self._apply_theme)

        tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(tabs)
        self._tabs = tabs

        # 启动时应用保存的主题
        saved_theme = self._settings_page._settings.get("theme", "system")
        self._apply_theme(saved_theme)

    def _on_tab_changed(self, index: int):
        widget = self._tabs.widget(index)
        if widget is self._build_page:
            self._build_page.refresh_group_refs()

    def _apply_theme(self, theme: str):
        app = QApplication.instance()
        if theme == "light":
            app.setStyle(QStyleFactory.create("Fusion"))
            app.setPalette(self._light_palette())
        elif theme == "dark":
            app.setStyle(QStyleFactory.create("Fusion"))
            app.setPalette(self._dark_palette())
        else:
            # 跟随系统
            app.setStyle(QStyleFactory.create("Fusion"))
            app.setPalette(app.style().standardPalette())

    @staticmethod
    def _dark_palette() -> QPalette:
        p = QPalette()
        p.setColor(QPalette.Window, QColor(45, 45, 48))
        p.setColor(QPalette.WindowText, QColor(212, 212, 212))
        p.setColor(QPalette.Base, QColor(30, 30, 30))
        p.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
        p.setColor(QPalette.ToolTipBase, QColor(45, 45, 48))
        p.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
        p.setColor(QPalette.Text, QColor(212, 212, 212))
        p.setColor(QPalette.Button, QColor(55, 55, 58))
        p.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        p.setColor(QPalette.BrightText, QColor(255, 255, 255))
        p.setColor(QPalette.Link, QColor(86, 156, 214))
        p.setColor(QPalette.Highlight, QColor(51, 102, 153))
        p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        p.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
        p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
        return p

    @staticmethod
    def _light_palette() -> QPalette:
        p = QPalette()
        p.setColor(QPalette.Window, QColor(240, 240, 240))
        p.setColor(QPalette.WindowText, QColor(30, 30, 30))
        p.setColor(QPalette.Base, QColor(255, 255, 255))
        p.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        p.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        p.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
        p.setColor(QPalette.Text, QColor(30, 30, 30))
        p.setColor(QPalette.Button, QColor(225, 225, 225))
        p.setColor(QPalette.ButtonText, QColor(30, 30, 30))
        p.setColor(QPalette.BrightText, QColor(0, 0, 0))
        p.setColor(QPalette.Link, QColor(0, 102, 204))
        p.setColor(QPalette.Highlight, QColor(0, 120, 215))
        p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        return p
