"""基于 SettingsService 的设置页。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, InfoBar, InfoBarPosition, LineEdit, PrimaryPushButton, PushButton, SwitchButton

from core.models.runtime import AppSettings
from services.settings_service import SettingsService


class SettingsPage(QWidget):
    settings_changed = Signal(object)
    steam_path_changed = Signal(str)

    def __init__(self, settings_service: SettingsService, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self.settings_service = settings_service
        self.settings = self.settings_service.get_settings()
        self._init_ui()
        self.update_from_settings(self.settings)

    def _init_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 设置页采用滚动布局，给开发者模式下的长表单留出足够扩展空间。
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        outer_layout.addWidget(scroll_area)

        scroll_content = QWidget(self)
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("设置", scroll_content)
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(self._create_general_settings())
        layout.addWidget(self._create_repo_settings())
        layout.addWidget(self._create_shop_settings())

        self.developer_card = self._create_developer_settings()
        layout.addWidget(self.developer_card)

        layout.addStretch(1)
        scroll_area.setWidget(scroll_content)

    def _create_general_settings(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("通用设置", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        steam_layout = QHBoxLayout()
        steam_label = QLabel("Steam安装目录:", card)
        steam_label.setFixedWidth(150)
        self.steam_input = LineEdit(card)
        self.steam_input.setPlaceholderText("留空自动检测（默认路径）")
        self.steam_input.editingFinished.connect(self._save_steam_path)
        steam_layout.addWidget(steam_label)
        steam_layout.addWidget(self.steam_input)

        self.steam_browse_button = PushButton("浏览", card)
        self.steam_browse_button.setFixedWidth(80)
        self.steam_browse_button.clicked.connect(self._browse_steam_path)
        steam_layout.addWidget(self.steam_browse_button)
        card_layout.addLayout(steam_layout)

        steam_desc = QLabel("用于读取Steam用户信息，留空时自动检测默认安装路径。", card)
        steam_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(steam_desc)

        return card

    def _create_repo_settings(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("仓库清理设置", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        favorited_layout = QHBoxLayout()
        favorited_label = QLabel("允许操作被收藏遗物:", card)
        favorited_label.setFixedWidth(150)
        self.allow_favorited_switch = SwitchButton(card)
        self.allow_favorited_switch.checkedChanged.connect(lambda value: self._save_settings(allow_operate_favorited=value))
        favorited_layout.addWidget(favorited_label)
        favorited_layout.addWidget(self.allow_favorited_switch)
        favorited_layout.addStretch(1)
        card_layout.addLayout(favorited_layout)

        valid_layout = QHBoxLayout()
        valid_label = QLabel("三有效模式:", card)
        valid_label.setFixedWidth(150)
        self.repo_require_triple_switch = SwitchButton(card)
        self.repo_require_triple_switch.checkedChanged.connect(lambda value: self._save_settings(require_double_valid=not value))
        valid_layout.addWidget(valid_label)
        valid_layout.addWidget(self.repo_require_triple_switch)
        valid_layout.addStretch(1)
        card_layout.addLayout(valid_layout)

        valid_desc = QLabel("开启: 3条词条匹配才合格 | 关闭: 2条词条匹配即合格", card)
        valid_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(valid_desc)

        return card

    def _create_shop_settings(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("商店筛选设置", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        valid_layout = QHBoxLayout()
        valid_label = QLabel("三有效模式:", card)
        valid_label.setFixedWidth(150)
        self.shop_require_triple_switch = SwitchButton(card)
        self.shop_require_triple_switch.checkedChanged.connect(lambda value: self._save_settings(shop_require_double_valid=not value))
        valid_layout.addWidget(valid_label)
        valid_layout.addWidget(self.shop_require_triple_switch)
        valid_layout.addStretch(1)
        card_layout.addLayout(valid_layout)

        valid_desc = QLabel("开启: 3条词条匹配才合格 | 关闭: 2条词条匹配即合格", card)
        valid_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(valid_desc)

        return card

    def _create_developer_settings(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("开发者设置", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        hint = QLabel("以下为高级选项，修改前请确认了解其影响。", card)
        hint.setStyleSheet("color: #e67e22; font-size: 8pt;")
        card_layout.addWidget(hint)

        ocr_layout = QHBoxLayout()
        ocr_label = QLabel("OCR调试模式:", card)
        ocr_label.setFixedWidth(150)
        self.ocr_debug_switch = SwitchButton(card)
        self.ocr_debug_switch.checkedChanged.connect(lambda value: self._save_settings(ocr_debug=value))
        ocr_layout.addWidget(ocr_label)
        ocr_layout.addWidget(self.ocr_debug_switch)
        ocr_layout.addStretch(1)
        card_layout.addLayout(ocr_layout)

        ocr_desc = QLabel("开启后保存OCR调试截图和识别结果。", card)
        ocr_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(ocr_desc)

        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("模板匹配阈值:", card)
        threshold_label.setFixedWidth(150)
        self.template_threshold_input = LineEdit(card)
        self.template_threshold_input.setFixedWidth(80)
        self.template_threshold_input.setValidator(QDoubleValidator(0.0, 1.0, 2, self))
        self.template_threshold_input.editingFinished.connect(self._save_template_threshold)
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.template_threshold_input)
        threshold_layout.addStretch(1)
        card_layout.addLayout(threshold_layout)

        threshold_desc = QLabel("商店模板匹配置信度阈值，默认0.7。", card)
        threshold_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(threshold_desc)

        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("亮度阈值:", card)
        brightness_label.setFixedWidth(150)
        self.brightness_threshold_input = LineEdit(card)
        self.brightness_threshold_input.setFixedWidth(80)
        self.brightness_threshold_input.setValidator(QIntValidator(0, 255, self))
        self.brightness_threshold_input.editingFinished.connect(self._save_brightness_threshold)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_threshold_input)
        brightness_layout.addStretch(1)
        card_layout.addLayout(brightness_layout)

        brightness_desc = QLabel("遗物亮暗状态判断使用的亮度阈值，默认45。", card)
        brightness_desc.setStyleSheet("color: gray; font-size: 8pt;")
        card_layout.addWidget(brightness_desc)

        sl_layout = QHBoxLayout()
        sl_label = QLabel("根据合格遗物数量停止:", card)
        sl_label.setFixedWidth(180)
        self.sl_mode_switch = SwitchButton(card)
        self.sl_mode_switch.checkedChanged.connect(lambda value: self._save_settings(sl_mode_enabled=value))
        sl_layout.addWidget(sl_label)
        sl_layout.addWidget(self.sl_mode_switch)
        sl_layout.addStretch(1)
        card_layout.addLayout(sl_layout)

        sl_desc = QLabel("开启后商店流程会根据目标合格遗物数量停止。", card)
        sl_desc.setStyleSheet("color: gray; font-size: 8pt;")
        sl_desc.setWordWrap(True)
        card_layout.addWidget(sl_desc)

        return card

    def update_from_settings(self, settings: AppSettings) -> None:
        self.settings = settings

        # 回填控件时临时屏蔽信号，避免 setText / setChecked 又反向触发一次保存。
        controls = [
            (self.steam_input, settings.steam_path, "setText"),
            (self.allow_favorited_switch, settings.allow_operate_favorited, "setChecked"),
            (self.repo_require_triple_switch, not settings.require_double_valid, "setChecked"),
            (self.shop_require_triple_switch, not settings.shop_require_double_valid, "setChecked"),
            (self.ocr_debug_switch, settings.ocr_debug, "setChecked"),
            (self.template_threshold_input, str(settings.template_threshold), "setText"),
            (self.brightness_threshold_input, str(settings.brightness_threshold), "setText"),
            (self.sl_mode_switch, settings.sl_mode_enabled, "setChecked"),
        ]

        for widget, value, method_name in controls:
            old_state = widget.blockSignals(True)
            getattr(widget, method_name)(value)
            widget.blockSignals(old_state)

        self.developer_card.setVisible(settings.developer_mode)

    def show_developer_settings(self) -> None:
        if self.developer_card.isVisible():
            return

        # 开发者模式一旦激活，同时写回设置，保证下次启动仍然可见。
        self.developer_card.setVisible(True)
        self._save_settings(developer_mode=True)
        InfoBar.success(
            title="开发者模式已激活",
            content="开发者设置已显示在设置页面底部。",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2500,
            parent=self,
        )

    def _browse_steam_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择 Steam 路径")
        if not path:
            return

        self.steam_input.setText(path)
        self._save_steam_path()

    def _save_steam_path(self) -> None:
        self._save_settings(steam_path=self.steam_input.text().strip())
        self.steam_path_changed.emit(self.settings.steam_path)

    def _save_template_threshold(self) -> None:
        text = self.template_threshold_input.text().strip()
        value = float(text) if text else 0.7
        self._save_settings(template_threshold=value)

    def _save_brightness_threshold(self) -> None:
        text = self.brightness_threshold_input.text().strip()
        value = int(text) if text else 45
        self._save_settings(brightness_threshold=value)

    def _save_settings(self, **changes) -> None:
        # 页面本身不拼装 JSON，只把变更字典交给 SettingsService 统一落盘。
        self.settings = self.settings_service.update_settings(**changes)
        self.update_from_settings(self.settings)
        self.settings_changed.emit(self.settings)
