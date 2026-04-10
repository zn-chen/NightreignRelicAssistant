"""独立预设管理页。"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, InfoBar, InfoBarPosition, PushButton

from services.preset_service import PresetService
from ui.components import PresetPanel


class PresetPage(QWidget):
    presets_changed = Signal()

    def __init__(self, preset_service: PresetService, parent=None):
        super().__init__(parent)
        self.setObjectName("PresetPage")
        self.preset_service = preset_service
        self.preset_panel = PresetPanel(preset_service, self)
        self.preset_panel.presets_modified.connect(self.presets_changed.emit)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(12)

        title = QLabel("预设管理", self)
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)

        description = QLabel("系统会按排序逐个尝试所有启用预设，直到命中，或全部未命中。", self)
        description.setStyleSheet("color: #666; font-size: 10pt;")
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addWidget(self._create_toolbar())
        layout.addWidget(self.preset_panel, 1)

    def _create_toolbar(self) -> CardWidget:
        card = CardWidget(self)
        card.setFixedHeight(60)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        hint = QLabel("导入会覆盖当前全部预设", card)
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint)
        layout.addStretch(1)

        export_button = PushButton("导出预设", card)
        export_button.setFixedWidth(110)
        export_button.clicked.connect(self._export_presets)
        layout.addWidget(export_button)

        import_button = PushButton("导入预设", card)
        import_button.setFixedWidth(110)
        import_button.clicked.connect(self._import_presets)
        layout.addWidget(import_button)
        return card

    def _export_presets(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "导出预设", "presets.json", "JSON Files (*.json)")
        if not path:
            return

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.preset_service.export_payload(), handle, ensure_ascii=False, indent=2)

        InfoBar.success(
            title="导出成功",
            content="预设文件已导出。",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2500,
            parent=self,
        )

    def _import_presets(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "导入预设", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.preset_service.import_payload(payload)
            self.preset_panel.refresh()
            self.presets_changed.emit()
            InfoBar.success(
                title="导入成功",
                content="预设配置已更新。",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2500,
                parent=self,
            )
        except Exception as exc:
            InfoBar.error(
                title="导入失败",
                content=str(exc),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3500,
                parent=self,
            )