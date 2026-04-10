"""存档管理页。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QMessageBox, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, InfoBar, InfoBarPosition, LineEdit as FluentLineEdit, PrimaryPushButton, PushButton

from services.save_service import SaveService
from ui.components import StableComboBox


class SavePage(QWidget):
    def __init__(self, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.setObjectName("SavePage")
        self.save_service = save_service
        self.current_steam_id = ""
        self._init_ui()
        self._refresh_all()

    def _init_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        outer_layout.addWidget(scroll_area)

        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("存档管理", content)
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(self._create_user_card())
        layout.addWidget(self._create_save_info_card())
        layout.addWidget(self._create_backup_card(), 1)

        scroll_area.setWidget(content)

    def _create_user_card(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("Steam 用户", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("选择用户:", card))

        self.user_combo = StableComboBox(card)
        self.user_combo.setFixedWidth(300)
        self.user_combo.currentIndexChanged.connect(self._on_user_changed)
        user_layout.addWidget(self.user_combo)
        user_layout.addStretch(1)
        card_layout.addLayout(user_layout)

        self.steam_status_label = QLabel(card)
        self.steam_status_label.setFont(QFont("Segoe UI", 8))
        self.steam_status_label.setStyleSheet("color: gray;")
        card_layout.addWidget(self.steam_status_label)

        return card

    def _create_save_info_card(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("当前存档", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        info_layout = QHBoxLayout()
        self.save_status_label = QLabel("存档状态: 检测中...", card)
        info_layout.addWidget(self.save_status_label)
        info_layout.addStretch(1)
        self.save_time_label = QLabel("", card)
        info_layout.addWidget(self.save_time_label)
        card_layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        self.backup_button = PrimaryPushButton("备份存档", card)
        self.backup_button.setFixedWidth(120)
        self.backup_button.clicked.connect(self._backup_save)
        button_layout.addWidget(self.backup_button)

        refresh_button = PushButton("刷新", card)
        refresh_button.setFixedWidth(80)
        refresh_button.clicked.connect(self._refresh_all)
        button_layout.addWidget(refresh_button)
        button_layout.addStretch(1)
        card_layout.addLayout(button_layout)

        return card

    def _create_backup_card(self) -> CardWidget:
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        title = QLabel("备份列表", card)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        card_layout.addWidget(title)

        scroll = QScrollArea(card)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.backup_list_widget = QWidget(card)
        self.backup_list_layout = QVBoxLayout(self.backup_list_widget)
        self.backup_list_layout.setContentsMargins(0, 0, 0, 0)
        self.backup_list_layout.setSpacing(8)
        self.backup_list_layout.addStretch(1)

        scroll.setWidget(self.backup_list_widget)
        card_layout.addWidget(scroll)
        return card

    def _refresh_all(self) -> None:
        # 用户、当前存档和备份列表三块状态一起刷新，避免页面显示互相不同步。
        self._populate_user_combo()
        self._refresh_save_info()
        self._refresh_backup_list()

    def _populate_user_combo(self) -> None:
        previous_id = self.current_steam_id
        users = self.save_service.get_users()
        most_recent_id = self.save_service.get_most_recent_user()

        # 这里优先保留当前选中用户，其次回退到最近登录用户，减少切换设置后的跳变。
        self.user_combo.blockSignals(True)
        self.user_combo.clear()

        if not users:
            self.user_combo.addItem("未检测到Steam用户", userData="")
            self.current_steam_id = ""
        else:
            default_index = 0
            for index, (steam_id, info) in enumerate(users.items()):
                display = f"{info['name']} ({steam_id})"
                if info.get("most_recent"):
                    display += " [最近登录]"
                self.user_combo.addItem(display, userData=steam_id)
                if steam_id == previous_id:
                    default_index = index
                elif not previous_id and steam_id == most_recent_id:
                    default_index = index

            self.user_combo.setCurrentIndex(default_index)
            self.current_steam_id = self.user_combo.itemData(default_index) or ""

        self.user_combo.blockSignals(False)
        self.steam_status_label.setText(f"Steam路径: {self.save_service.steam_path or '未检测到，请在设置中配置'}")

    def _on_user_changed(self) -> None:
        self.current_steam_id = self.user_combo.itemData(self.user_combo.currentIndex()) or ""
        self._refresh_save_info()
        self._refresh_backup_list()

    def _refresh_save_info(self) -> None:
        if not self.current_steam_id:
            self.save_status_label.setText("存档状态: 未选择用户")
            self.save_time_label.setText("")
            self.backup_button.setEnabled(False)
            return

        info = self.save_service.get_save_info(self.current_steam_id)
        if info["exists"]:
            size_mb = info["size"] / (1024 * 1024)
            self.save_status_label.setText(f"存档状态: 已找到 ({size_mb:.1f} MB)")
            self.save_time_label.setText(f"最后修改: {info['modified_time']}")
            self.backup_button.setEnabled(True)
        else:
            self.save_status_label.setText("存档状态: 未找到存档文件")
            self.save_time_label.setText("")
            self.backup_button.setEnabled(False)

    def _refresh_backup_list(self) -> None:
        # 先清空旧卡片，再按当前 Steam 用户重新生成备份行。
        while self.backup_list_layout.count() > 1:
            item = self.backup_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.current_steam_id:
            return

        backups = self.save_service.get_backups(self.current_steam_id)
        if not backups:
            placeholder = QLabel("暂无备份", self.backup_list_widget)
            placeholder.setStyleSheet("color: gray;")
            placeholder.setAlignment(Qt.AlignCenter)
            self.backup_list_layout.insertWidget(0, placeholder)
            return

        for backup in backups:
            self.backup_list_layout.insertWidget(self.backup_list_layout.count() - 1, self._create_backup_row(backup))

    def _create_backup_row(self, backup: dict) -> QWidget:
        row = QWidget(self.backup_list_widget)
        row.setStyleSheet("QWidget { background-color: #f8f8f8; border-radius: 6px; padding: 4px; }")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(12)

        name_label = QLabel(backup["display_name"], row)
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setMinimumWidth(150)
        row_layout.addWidget(name_label)

        time_label = QLabel(backup["modified_time"], row)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: gray;")
        row_layout.addWidget(time_label)

        size_mb = backup["size"] / (1024 * 1024)
        size_label = QLabel(f"{size_mb:.1f} MB", row)
        size_label.setFont(QFont("Segoe UI", 8))
        size_label.setStyleSheet("color: gray;")
        size_label.setFixedWidth(60)
        row_layout.addWidget(size_label)

        row_layout.addStretch(1)

        restore_button = PrimaryPushButton("恢复", row)
        restore_button.setFixedSize(60, 28)
        restore_button.clicked.connect(lambda _checked=False, item=backup: self._restore_backup(item))
        row_layout.addWidget(restore_button)

        rename_button = PushButton("重命名", row)
        rename_button.setFixedSize(70, 28)
        rename_button.clicked.connect(lambda _checked=False, item=backup: self._rename_backup(item))
        row_layout.addWidget(rename_button)

        delete_button = PushButton("删除", row)
        delete_button.setFixedSize(60, 28)
        delete_button.clicked.connect(lambda _checked=False, item=backup: self._delete_backup(item))
        row_layout.addWidget(delete_button)

        return row

    def _backup_save(self) -> None:
        if not self.current_steam_id:
            return

        # 备份/重命名都用轻量对话框收集字符串，避免为了单字段操作再开整页编辑器。
        dialog = QDialog(self)
        dialog.setWindowTitle("备份存档")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.addWidget(QLabel("输入备份名称（留空使用时间戳）:", dialog))

        line_edit = FluentLineEdit(dialog)
        layout.addWidget(line_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        success, message = self.save_service.backup_save(self.current_steam_id, line_edit.text().strip())
        self._show_result(success, message)
        self._refresh_backup_list()

    def _restore_backup(self, backup: dict) -> None:
        if not self.current_steam_id:
            return
        if QMessageBox.question(self, "确认恢复", f"确定恢复备份 {backup['display_name']} 吗？") != QMessageBox.Yes:
            return

        success, message = self.save_service.restore_save(self.current_steam_id, backup["path"])
        self._show_result(success, message)
        self._refresh_all()

    def _rename_backup(self, backup: dict) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("重命名备份")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.addWidget(QLabel("输入新名称:", dialog))

        line_edit = FluentLineEdit(dialog)
        line_edit.setText(backup["display_name"])
        layout.addWidget(line_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        success, message = self.save_service.rename_backup(backup["path"], line_edit.text().strip())
        self._show_result(success, message)
        self._refresh_backup_list()

    def _delete_backup(self, backup: dict) -> None:
        if QMessageBox.question(self, "确认删除", f"确定删除备份 {backup['display_name']} 吗？") != QMessageBox.Yes:
            return

        success, message = self.save_service.delete_backup(backup["path"])
        self._show_result(success, message)
        self._refresh_backup_list()

    def _show_result(self, success: bool, message: str) -> None:
        # 存档页统一使用 InfoBar 回馈结果，不再额外弹同步阻塞弹窗。
        if success:
            InfoBar.success(
                title="操作成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2500,
                parent=self,
            )
            return

        InfoBar.error(
            title="操作失败",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def update_steam_path(self, steam_path: str) -> None:
        self.save_service.set_steam_path(steam_path)
        self.current_steam_id = self.save_service.get_most_recent_user()
        self._refresh_all()
