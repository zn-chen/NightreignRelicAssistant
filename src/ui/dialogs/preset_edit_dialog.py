"""预设编辑对话框。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import LineEdit, PrimaryPushButton, PushButton, SegmentedWidget, isDarkTheme


class PresetEditDialog(QDialog):
    FORM_LABEL_WIDTH = 60

    def __init__(
        self,
        *,
        title: str,
        normal_relic_vocabulary: list[str],
        deepnight_relic_vocabulary: list[str],
        blacklist_vocabulary: list[str],
        preset_name: str = "",
        selected_normal_relic_affixes: list[str] | None = None,
        selected_deepnight_relic_affixes: list[str] | None = None,
        selected_blacklist_affixes: list[str] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.result_payload: dict | None = None

        self.setWindowTitle(title)
        self.setMinimumSize(760, 620)

        self._init_ui(
            preset_name,
            normal_relic_vocabulary,
            deepnight_relic_vocabulary,
            blacklist_vocabulary,
            selected_normal_relic_affixes or [],
            selected_deepnight_relic_affixes or [],
            selected_blacklist_affixes or [],
        )

    def _init_ui(
        self,
        preset_name: str,
        normal_relic_vocabulary: list[str],
        deepnight_relic_vocabulary: list[str],
        blacklist_vocabulary: list[str],
        selected_normal_relic_affixes: list[str],
        selected_deepnight_relic_affixes: list[str],
        selected_blacklist_affixes: list[str],
    ) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        name_row = QHBoxLayout()
        name_label = QLabel("预设名称:")
        name_label.setFixedWidth(80)
        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("输入预设名称")
        self.name_input.setText(preset_name)
        name_row.addWidget(name_label)
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)

        # 三类词条共用一套构建逻辑，再通过分段控件切换内容栈，避免重复页面代码。
        normal_tab, self.normal_relic_list, self.normal_relic_count_label = self._build_affix_tab(
            vocabulary=normal_relic_vocabulary,
            selected_affixes=selected_normal_relic_affixes,
            search_placeholder="搜索普通遗物词条",
        )
        deepnight_tab, self.deepnight_relic_list, self.deepnight_relic_count_label = self._build_affix_tab(
            vocabulary=deepnight_relic_vocabulary,
            selected_affixes=selected_deepnight_relic_affixes,
            search_placeholder="搜索深夜遗物词条",
        )
        blacklist_tab, self.blacklist_list, self.blacklist_count_label = self._build_affix_tab(
            vocabulary=blacklist_vocabulary,
            selected_affixes=selected_blacklist_affixes,
            search_placeholder="搜索黑名单词条",
        )

        self.segmented_widget = SegmentedWidget(self)
        self.segmented_widget.setObjectName("presetSegmentedWidget")
        self.segmented_widget.setItemFontSize(13)
        self._section_indexes = {
            "normal": 0,
            "deepnight": 1,
            "blacklist": 2,
        }
        self.segmented_widget.addItem("normal", "普通遗物词条")
        self.segmented_widget.addItem("deepnight", "深夜遗物词条")
        self.segmented_widget.addItem("blacklist", "黑名单词条")
        self.segmented_widget.currentItemChanged.connect(self._on_section_changed)

        segmented_row = QHBoxLayout()
        segmented_row.setContentsMargins(0, 0, 0, 0)
        segmented_row.addWidget(self.segmented_widget)
        segmented_row.addStretch(1)
        layout.addLayout(segmented_row)

        self.content_panel = QWidget(self)
        self.content_panel.setObjectName("affixContentPanel")
        self._apply_content_panel_stylesheet(self.content_panel)

        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.section_stack = QStackedWidget(self.content_panel)
        self.section_stack.setObjectName("affixSectionStack")
        self.section_stack.addWidget(normal_tab)
        self.section_stack.addWidget(deepnight_tab)
        self.section_stack.addWidget(blacklist_tab)
        content_layout.addWidget(self.section_stack)

        layout.addWidget(self.content_panel, 1)
        self.segmented_widget.setCurrentItem("normal")

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.status_label)
        self._update_status()

        footer = QHBoxLayout()
        footer.addStretch(1)

        cancel_button = PushButton("取消")
        cancel_button.clicked.connect(self.reject)
        footer.addWidget(cancel_button)

        save_button = PrimaryPushButton("保存")
        save_button.clicked.connect(self._save)
        footer.addWidget(save_button)
        layout.addLayout(footer)

    def _build_affix_tab(
        self,
        *,
        vocabulary: list[str],
        selected_affixes: list[str],
        search_placeholder: str,
    ) -> tuple[QWidget, QListWidget, QLabel]:
        tab = QWidget(self)
        tab.setObjectName("affixTabPage")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        search_label = QLabel("搜索:")
        search_label.setFixedWidth(self.FORM_LABEL_WIDTH)
        search_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        search_input = LineEdit()
        search_input.setPlaceholderText(search_placeholder)
        search_input.setFixedHeight(32)
        search_row.addWidget(search_label)
        search_row.addWidget(search_input)
        layout.addLayout(search_row)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        batch_label = QLabel("批量操作:")
        batch_label.setFixedWidth(self.FORM_LABEL_WIDTH)
        batch_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        actions.addWidget(batch_label)

        # 列表项直接存储勾选状态，保存时只需把所有已选项重新收集出来即可。
        list_widget = QListWidget(tab)
        self._apply_list_stylesheet(list_widget)
        selected_set = set(selected_affixes)
        for affix in vocabulary:
            item = QListWidgetItem(affix)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if affix in selected_set else Qt.Unchecked)
            list_widget.addItem(item)

        for label, handler in [
            ("全选", lambda: self._set_visible_items_check_state(list_widget, Qt.Checked)),
            ("全不选", lambda: self._set_visible_items_check_state(list_widget, Qt.Unchecked)),
            ("反选", lambda: self._invert_visible_items(list_widget)),
        ]:
            button = PushButton(label)
            button.setFixedWidth(80)
            button.setFixedHeight(32)
            button.clicked.connect(handler)
            actions.addWidget(button)
        actions.addStretch(1)
        layout.addLayout(actions)

        list_label = QLabel(f"词条列表 (共 {len(vocabulary)} 条):")
        list_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(list_label)
        layout.addWidget(list_widget, 1)

        count_label = QLabel(tab)
        count_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(count_label)

        search_input.textChanged.connect(lambda text: self._apply_filter(list_widget, text))
        list_widget.itemChanged.connect(lambda *_args: self._update_count(list_widget, count_label))
        self._update_count(list_widget, count_label)
        return tab, list_widget, count_label

    def _apply_content_panel_stylesheet(self, panel: QWidget) -> None:
        if isDarkTheme():
            stylesheet = """
                QWidget#affixContentPanel {
                    border: 1px solid #3d3d3d;
                    border-radius: 10px;
                    background-color: #222222;
                }
                QStackedWidget#affixSectionStack {
                    background: transparent;
                }
                QWidget#affixTabPage {
                    background: transparent;
                }
            """
        else:
            stylesheet = """
                QWidget#affixContentPanel {
                    border: 1px solid #dddddd;
                    border-radius: 10px;
                    background-color: #f7f7f7;
                }
                QStackedWidget#affixSectionStack {
                    background: transparent;
                }
                QWidget#affixTabPage {
                    background: transparent;
                }
            """
        panel.setStyleSheet(stylesheet)

    def _on_section_changed(self, route_key: str) -> None:
        self.section_stack.setCurrentIndex(self._section_indexes[route_key])

    def _apply_list_stylesheet(self, list_widget: QListWidget) -> None:
        if isDarkTheme():
            stylesheet = """
                QListWidget {
                    border: 1px solid #3d3d3d;
                    border-radius: 6px;
                    background-color: #1e1e1e;
                    outline: none;
                    padding: 4px;
                }
                QListWidget::item {
                    height: 38px;
                    padding-left: 8px;
                    color: #e0e0e0;
                    border-radius: 4px;
                    margin-bottom: 2px;
                }
                QListWidget::item:hover {
                    background-color: #2d2d2d;
                }
                QListWidget::item:selected {
                    background-color: #1a3a52;
                    color: #e0e0e0;
                }
                QListWidget::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 1px solid #555555;
                    background-color: #2d2d2d;
                    margin-right: 12px;
                }
                QListWidget::indicator:hover {
                    border-color: #009faa;
                    background-color: #3d3d3d;
                }
                QListWidget::indicator:checked {
                    background-color: #009faa;
                    border: 1px solid #009faa;
                    image: url(":/qfluentwidgets/images/check_box_checked_white.png");
                }
            """
        else:
            stylesheet = """
                QListWidget {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    background-color: white;
                    outline: none;
                    padding: 4px;
                }
                QListWidget::item {
                    height: 38px;
                    padding-left: 8px;
                    color: #333;
                    border-radius: 4px;
                    margin-bottom: 2px;
                }
                QListWidget::item:hover {
                    background-color: #f5f5f5;
                }
                QListWidget::item:selected {
                    background-color: #e3f2fd;
                    color: #000;
                }
                QListWidget::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 1px solid #c0c0c0;
                    background-color: white;
                    margin-right: 12px;
                }
                QListWidget::indicator:hover {
                    border-color: #009faa;
                    background-color: #f0f8ff;
                }
                QListWidget::indicator:checked {
                    background-color: #009faa;
                    border: 1px solid #009faa;
                    image: url(":/qfluentwidgets/images/check_box_checked_white.png");
                }
            """
        list_widget.setStyleSheet(stylesheet)

    def _apply_filter(self, list_widget: QListWidget, text: str) -> None:
        # 过滤只影响可见性，不改勾选状态，避免搜索时误丢用户已选结果。
        lowered = text.lower()
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setHidden(lowered not in item.text().lower())

    def _set_visible_items_check_state(self, list_widget: QListWidget, state: Qt.CheckState) -> None:
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if not item.isHidden():
                item.setCheckState(state)

    def _invert_visible_items(self, list_widget: QListWidget) -> None:
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if item.isHidden():
                continue
            item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)

    def _update_count(self, list_widget: QListWidget, count_label: QLabel) -> None:
        selected = sum(1 for index in range(list_widget.count()) if list_widget.item(index).checkState() == Qt.Checked)
        count_label.setText(f"已选择: {selected} 条")
        self._update_status()

    def _update_status(self) -> None:
        if not hasattr(self, "status_label"):
            return
        normal_count = self._checked_items(self.normal_relic_list) if hasattr(self, "normal_relic_list") else []
        deepnight_count = self._checked_items(self.deepnight_relic_list) if hasattr(self, "deepnight_relic_list") else []
        blacklist_count = self._checked_items(self.blacklist_list) if hasattr(self, "blacklist_list") else []
        self.status_label.setText(
            f"当前选择: 普通 {len(normal_count)} 条 | 深夜 {len(deepnight_count)} 条 | 黑名单 {len(blacklist_count)} 条"
        )
        self.status_label.setStyleSheet("color: #666; font-size: 9pt;")

    def _checked_items(self, list_widget: QListWidget) -> list[str]:
        values = []
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if item.checkState() == Qt.Checked:
                values.append(item.text())
        return values

    def _save(self) -> None:
        if not self.name_input.text().strip():
            self.status_label.setText("请输入预设名称")
            self.status_label.setStyleSheet("color: #dc2626; font-size: 9pt;")
            return

        # 对话框只回传结构化 payload，真正创建或更新预设由外层面板决定。
        self.result_payload = {
            "name": self.name_input.text().strip(),
            "normal_relic_affixes": self._checked_items(self.normal_relic_list),
            "deepnight_relic_affixes": self._checked_items(self.deepnight_relic_list),
            "blacklist_affixes": self._checked_items(self.blacklist_list),
        }
        self.accept()
