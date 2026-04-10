"""独立的预设管理面板。"""

from __future__ import annotations

from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, PrimaryPushButton, PushButton

from core.models.preset import PresetRecord
from services.preset_service import PresetService
from ui.dialogs.preset_edit_dialog import PresetEditDialog


class DragDropContainer(QWidget):
    reorder_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

    def add_card(self, card: QWidget) -> None:
        # 通过覆写卡片的鼠标/拖放事件，为现有卡片列表补一个轻量拖拽排序层。
        original_mouse_press = card.mousePressEvent
        original_mouse_move = card.mouseMoveEvent

        def mouse_press(event):
            if event.button() == Qt.LeftButton:
                card._drag_start_pos = event.position().toPoint()
            original_mouse_press(event)

        def mouse_move(event):
            if getattr(card, "_drag_start_pos", None) is not None and event.buttons() == Qt.LeftButton:
                distance = (event.position().toPoint() - card._drag_start_pos).manhattanLength()
                if distance > 20:
                    mime_data = QMimeData()
                    mime_data.setText(card.preset_id)
                    drag = QDrag(card)
                    drag.setMimeData(mime_data)
                    drag.exec(Qt.MoveAction)
            original_mouse_move(event)

        def drag_enter(event):
            if event.mimeData().hasText():
                event.acceptProposedAction()
            else:
                event.ignore()

        def drop(event):
            if event.mimeData().hasText():
                source_id = event.mimeData().text()
                target_id = card.preset_id
                if source_id != target_id:
                    self.reorder_requested.emit(source_id, target_id)
                event.acceptProposedAction()
            else:
                event.ignore()

        card.setAcceptDrops(True)
        card.mousePressEvent = mouse_press
        card.mouseMoveEvent = mouse_move
        card.dragEnterEvent = drag_enter
        card.dropEvent = drop
        self.layout.addWidget(card)


class PresetCard(CardWidget):
    edit_clicked = Signal(str)
    delete_clicked = Signal(str)
    toggle_clicked = Signal(str)

    def __init__(self, preset: PresetRecord, parent=None):
        super().__init__(parent)
        self.preset = preset
        self.preset_id = preset.preset_id
        self._expanded = False
        self._drag_start_pos = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.expand_button = QPushButton("▶")
        self.expand_button.setFixedSize(20, 20)
        self.expand_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background: transparent;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.06);
                border-radius: 3px;
            }
            """
        )
        self.expand_button.clicked.connect(self._toggle_expand)
        top_layout.addWidget(self.expand_button)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title_label = QLabel(self.preset.name)
        title_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        info_layout.addWidget(title_label)

        subtitle_label = QLabel(
            f"普通 {len(self.preset.normal_relic_affixes)} 条 | 深夜 {len(self.preset.deepnight_relic_affixes)} 条 | 黑名单 {len(self.preset.blacklist_affixes)} 条"
        )
        subtitle_label.setStyleSheet("color: #888; font-size: 9pt;")
        info_layout.addWidget(subtitle_label)
        top_layout.addLayout(info_layout)
        top_layout.addStretch(1)

        self.active_checkbox = QCheckBox("启用")
        self.active_checkbox.setChecked(self.preset.enabled)
        self.active_checkbox.stateChanged.connect(lambda _state: self.toggle_clicked.emit(self.preset_id))
        top_layout.addWidget(self.active_checkbox)

        edit_button = PushButton("编辑")
        edit_button.setFixedWidth(60)
        edit_button.clicked.connect(lambda: self.edit_clicked.emit(self.preset_id))
        top_layout.addWidget(edit_button)

        delete_button = PushButton("删除")
        delete_button.setFixedWidth(60)
        delete_button.clicked.connect(lambda: self.delete_clicked.emit(self.preset_id))
        top_layout.addWidget(delete_button)

        layout.addLayout(top_layout)

        self.affixes_widget = QWidget(self)
        affixes_layout = QVBoxLayout(self.affixes_widget)
        affixes_layout.setContentsMargins(24, 4, 4, 4)
        affixes_layout.setSpacing(8)

        affixes_layout.addWidget(self._build_affix_group("普通遗物词条", self.preset.normal_relic_affixes))
        affixes_layout.addWidget(self._build_affix_group("深夜遗物词条", self.preset.deepnight_relic_affixes))
        affixes_layout.addWidget(self._build_affix_group("黑名单词条", self.preset.blacklist_affixes))

        self.affixes_widget.setVisible(False)
        layout.addWidget(self.affixes_widget)

    def _build_affix_group(self, title: str, affixes: list[str]) -> QWidget:
        container = QWidget(self.affixes_widget)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(title, container)
        title_label.setStyleSheet("font-size: 9pt; font-weight: bold; color: #666;")
        layout.addWidget(title_label)

        preview = affixes[:12]
        if not preview:
            empty_label = QLabel("未设置", container)
            empty_label.setStyleSheet("color: #999; font-size: 9pt;")
            layout.addWidget(empty_label)
            return container

        for affix in preview:
            affix_label = QLabel(f"• {affix}", container)
            affix_label.setWordWrap(True)
            affix_label.setStyleSheet("color: #555; font-size: 9pt;")
            layout.addWidget(affix_label)

        if len(affixes) > len(preview):
            more_label = QLabel(f"... 还有 {len(affixes) - len(preview)} 条", container)
            more_label.setStyleSheet("color: #999; font-size: 9pt; font-style: italic;")
            layout.addWidget(more_label)

        return container

    def _toggle_expand(self) -> None:
        self._expanded = not self._expanded
        self.expand_button.setText("▼" if self._expanded else "▶")
        self.affixes_widget.setVisible(self._expanded)


class PresetPanel(QWidget):
    presets_modified = Signal()

    def __init__(self, preset_service: PresetService, parent=None):
        super().__init__(parent)
        self.preset_service = preset_service
        self._cards_container = QWidget(self)
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(8)
        self._init_ui()
        self.refresh()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._cards_container)
        layout.addWidget(scroll, 1)

    def refresh(self) -> None:
        # 每次刷新都重建卡片树，保证排序、启停和内容变更后界面状态完全一致。
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        presets = self.preset_service.list_presets()
        if presets:
            container = DragDropContainer(self)
            container.reorder_requested.connect(self._handle_reorder)
            for preset in presets:
                card = PresetCard(preset, self)
                card.edit_clicked.connect(self._edit_preset_by_id)
                card.delete_clicked.connect(self._delete_preset_by_id)
                card.toggle_clicked.connect(self._toggle_preset_by_id)
                container.add_card(card)
            self._cards_layout.addWidget(container)
        else:
            placeholder = QLabel("暂无预设，请先创建。", self)
            placeholder.setStyleSheet("color: gray; padding: 12px 4px;")
            self._cards_layout.addWidget(placeholder)

        add_button = PrimaryPushButton("+ 创建预设")
        add_button.setFixedHeight(32)
        add_button.clicked.connect(self._create_preset)
        self._cards_layout.addWidget(add_button)
        self._cards_layout.addStretch(1)

    def _open_dialog(self, *, title: str, preset: PresetRecord | None = None) -> PresetEditDialog:
        # 编辑与创建共用同一个对话框，只在这里决定是否注入既有预设内容。
        return PresetEditDialog(
            title=title,
            preset_name=preset.name if preset is not None else "",
            normal_relic_vocabulary=self.preset_service.load_vocabulary("normal_relic"),
            deepnight_relic_vocabulary=self.preset_service.load_vocabulary("deepnight_relic"),
            blacklist_vocabulary=self.preset_service.load_vocabulary("blacklist"),
            selected_normal_relic_affixes=preset.normal_relic_affixes if preset is not None else [],
            selected_deepnight_relic_affixes=preset.deepnight_relic_affixes if preset is not None else [],
            selected_blacklist_affixes=preset.blacklist_affixes if preset is not None else [],
            parent=self,
        )

    def _handle_reorder(self, source_id: str, target_id: str) -> None:
        self.preset_service.reorder_presets(source_id, target_id)
        self.refresh()
        self.presets_modified.emit()

    def _create_preset(self) -> None:
        dialog = self._open_dialog(title="创建预设")
        if dialog.exec() and dialog.result_payload is not None:
            try:
                payload = dialog.result_payload
                self.preset_service.create_preset(
                    payload["name"],
                    payload["normal_relic_affixes"],
                    payload["deepnight_relic_affixes"],
                    payload["blacklist_affixes"],
                )
                self.refresh()
                self.presets_modified.emit()
            except Exception as exc:
                QMessageBox.warning(self, "操作失败", str(exc))

    def _edit_preset_by_id(self, preset_id: str) -> None:
        preset = self.preset_service.get_preset(preset_id)
        if preset is None:
            return

        dialog = self._open_dialog(title="编辑预设", preset=preset)
        if dialog.exec() and dialog.result_payload is not None:
            payload = dialog.result_payload
            self.preset_service.update_preset(
                preset.preset_id,
                name=payload["name"],
                normal_relic_affixes=payload["normal_relic_affixes"],
                deepnight_relic_affixes=payload["deepnight_relic_affixes"],
                blacklist_affixes=payload["blacklist_affixes"],
            )
            self.refresh()
            self.presets_modified.emit()

    def _toggle_preset_by_id(self, preset_id: str) -> None:
        self.preset_service.toggle_preset_enabled(preset_id)
        self.refresh()
        self.presets_modified.emit()

    def _delete_preset_by_id(self, preset_id: str) -> None:
        preset = self.preset_service.get_preset(preset_id)
        if preset is None:
            return

        if QMessageBox.question(self, "确认删除", f"确定删除预设 {preset.name} 吗？") != QMessageBox.Yes:
            return

        self.preset_service.delete_preset(preset_id)
        self.refresh()
        self.presets_modified.emit()
