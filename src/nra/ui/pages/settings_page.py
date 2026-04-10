"""设置页面"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QCheckBox,
)
from nra.ui.widgets.helpers import make_card


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
        return {
            "steam_path": "",
            "backup_dir": "",
            "dingtalk_enabled": False,
            "dingtalk_webhook": "",
        }

    def _save(self):
        os.makedirs(os.path.dirname(self._settings_path) or ".", exist_ok=True)
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(12)

        # 存档备份
        backup_card, backup_layout = make_card("存档备份")

        steam_row = QHBoxLayout()
        steam_row.addWidget(QLabel("Steam 路径:"))
        self._steam_path_input = QLineEdit(self._settings.get("steam_path", ""))
        self._steam_path_input.setPlaceholderText("Steam 安装目录")
        self._steam_path_input.editingFinished.connect(self._on_steam_path_changed)
        steam_row.addWidget(self._steam_path_input)
        steam_browse = QPushButton("浏览")
        steam_browse.clicked.connect(self._browse_steam_path)
        steam_row.addWidget(steam_browse)
        backup_layout.addLayout(steam_row)

        backup_row = QHBoxLayout()
        backup_row.addWidget(QLabel("备份目录:"))
        self._backup_dir_input = QLineEdit(self._settings.get("backup_dir", ""))
        self._backup_dir_input.setPlaceholderText("存档备份保存位置")
        self._backup_dir_input.editingFinished.connect(self._on_backup_dir_changed)
        backup_row.addWidget(self._backup_dir_input)
        backup_browse = QPushButton("浏览")
        backup_browse.clicked.connect(self._browse_backup_dir)
        backup_row.addWidget(backup_browse)
        backup_layout.addLayout(backup_row)

        layout.addWidget(backup_card)

        # 出货通知
        notify_card, notify_layout = make_card("出货通知")

        self._dingtalk_cb = QCheckBox("启用钉钉通知")
        self._dingtalk_cb.setChecked(self._settings.get("dingtalk_enabled", False))
        self._dingtalk_cb.stateChanged.connect(self._on_dingtalk_toggled)
        notify_layout.addWidget(self._dingtalk_cb)

        webhook_row = QHBoxLayout()
        webhook_row.addWidget(QLabel("Webhook:"))
        self._webhook_input = QLineEdit(self._settings.get("dingtalk_webhook", ""))
        self._webhook_input.setPlaceholderText("钉钉机器人 Webhook 地址")
        self._webhook_input.editingFinished.connect(self._on_webhook_changed)
        webhook_row.addWidget(self._webhook_input)
        notify_layout.addLayout(webhook_row)

        layout.addWidget(notify_card)

        layout.addStretch()

    def _browse_steam_path(self):
        d = QFileDialog.getExistingDirectory(self, "选择 Steam 目录")
        if d:
            self._steam_path_input.setText(d)
            self._on_steam_path_changed()

    def _browse_backup_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if d:
            self._backup_dir_input.setText(d)
            self._on_backup_dir_changed()

    def _on_steam_path_changed(self):
        self._settings["steam_path"] = self._steam_path_input.text()
        self._save()

    def _on_backup_dir_changed(self):
        self._settings["backup_dir"] = self._backup_dir_input.text()
        self._save()

    def _on_dingtalk_toggled(self, state):
        self._settings["dingtalk_enabled"] = bool(state)
        self._save()

    def _on_webhook_changed(self):
        self._settings["dingtalk_webhook"] = self._webhook_input.text()
        self._save()
