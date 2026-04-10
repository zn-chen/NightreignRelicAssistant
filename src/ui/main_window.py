"""应用主窗口。"""

from __future__ import annotations

from PySide6.QtGui import QCloseEvent
from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition, Theme, setTheme

from app.container import AppContainer
from ui.config import NAVIGATION_CONFIG, THEME_CONFIG, WINDOW_CONFIG
from ui.dialogs import WelcomeDialog
from ui.pages import AboutPage, PresetPage, RepoPage, SavePage, SettingsPage, ShopPage
from ui.workers import OCRInitWorker


class MainWindow(FluentWindow):
    def __init__(self, container: AppContainer):
        super().__init__()
        self.container = container

        self.setWindowTitle(WINDOW_CONFIG["title"])
        self.resize(WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.setMinimumSize(WINDOW_CONFIG["min_width"], WINDOW_CONFIG["min_height"])

        # 页面和后台初始化线程都在主窗口阶段一次性创建，避免切页时反复构造。
        self.shop_page = ShopPage(container.history_service, container.shop_service)
        self.repo_page = RepoPage(container.history_service, container.repo_service)
        self.preset_page = PresetPage(container.preset_service)
        self.save_page = SavePage(container.save_service)
        self.settings_page = SettingsPage(container.settings_service)
        self.about_page = AboutPage()
        self.init_worker = OCRInitWorker(container.ocr_service, self)

        self._apply_theme(container.settings_service.get_settings().theme)
        self._optimize_navigation()
        self._init_pages()
        self._wire_signals()
        self._subscribe_logs()
        self._apply_settings()
        self._start_ocr_initialization()

    def _apply_theme(self, theme_name: str) -> None:
        effective_theme = theme_name if theme_name in {"light", "dark"} else THEME_CONFIG["theme"]
        setTheme(Theme.DARK if effective_theme == "dark" else Theme.LIGHT)

    def _optimize_navigation(self) -> None:
        self.navigationInterface.setAcrylicEnabled(NAVIGATION_CONFIG["acrylic_enabled"])

    def _init_pages(self) -> None:
        self.addSubInterface(self.shop_page, FluentIcon.SHOPPING_CART, "商店筛选", NavigationItemPosition.TOP)
        self.addSubInterface(self.repo_page, FluentIcon.FOLDER, "仓库清理", NavigationItemPosition.TOP)
        self.addSubInterface(self.preset_page, FluentIcon.ADD, "预设管理", NavigationItemPosition.TOP)
        self.addSubInterface(self.save_page, FluentIcon.SAVE, "存档管理", NavigationItemPosition.TOP)
        self.addSubInterface(self.settings_page, FluentIcon.SETTING, "设置", NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_page, FluentIcon.INFO, "关于", NavigationItemPosition.BOTTOM)

    def _wire_signals(self) -> None:
        # 主窗口负责把页面之间的跨模块联动统一串起来，页面自身只关注本页职责。
        self.preset_page.presets_changed.connect(self._refresh_presets_everywhere)
        self.settings_page.settings_changed.connect(self._on_settings_changed)
        self.settings_page.steam_path_changed.connect(self.save_page.update_steam_path)
        self.about_page.developer_mode_activated.connect(self.settings_page.show_developer_settings)
        self.init_worker.succeeded.connect(self._on_ocr_ready)
        self.init_worker.failed.connect(self._on_ocr_failed)

    def _subscribe_logs(self) -> None:
        self.container.logger.subscribe(self.shop_page.logger.log)
        self.container.logger.subscribe(self.repo_page.logger.log)

    def _apply_settings(self) -> None:
        # 设置加载后一次性分发到各页面，避免每个页面重复读取仓储。
        settings = self.container.settings_service.get_settings()
        self._apply_theme(settings.theme)
        self.shop_page.update_settings(settings)
        self.repo_page.update_settings(settings)
        self.settings_page.update_from_settings(settings)
        self.save_page.update_steam_path(settings.steam_path)

    def _start_ocr_initialization(self) -> None:
        # OCR 初始化放到后台线程执行，避免主窗口首次显示时卡住界面。
        self.container.logger.info("开始初始化 OCR 服务")
        self.init_worker.start()

    def _on_ocr_ready(self) -> None:
        self.container.logger.info("OCR 服务初始化完成")
        self.shop_page.set_ocr_ready(True)
        self.repo_page.set_ocr_ready(True)

    def _on_ocr_failed(self, error: str) -> None:
        self.container.logger.error(f"OCR 服务初始化失败: {error}")

    def _refresh_presets_everywhere(self) -> None:
        self.container.preset_service.reload()
        self.preset_page.preset_panel.refresh()

    def _on_settings_changed(self, settings) -> None:
        self._apply_theme(settings.theme)
        self.shop_page.update_settings(settings)
        self.repo_page.update_settings(settings)
        self.save_page.update_steam_path(settings.steam_path)

    def maybe_show_welcome(self) -> None:
        settings = self.container.settings_service.get_settings()
        if not settings.show_welcome:
            return

        dialog = WelcomeDialog(self)
        dialog.exec()
        if dialog.should_hide_forever():
            self.container.settings_service.update_settings(show_welcome=False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.init_worker.isRunning():
            self.init_worker.wait(2000)
        super().closeEvent(event)
