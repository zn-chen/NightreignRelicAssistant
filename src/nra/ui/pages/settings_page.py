"""设置页面"""

import json
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QListWidgetItem, QInputDialog,
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    PushButton, CheckBox, LineEdit, BodyLabel,
    ComboBox, ListWidget, MessageBox,
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
            "backup_dir": "data/save_backups",
            "dingtalk_enabled": False,
            "dingtalk_webhook": "",
        }

    def _save_settings(self):
        os.makedirs(os.path.dirname(self._settings_path) or ".", exist_ok=True)
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(12)

        # 出货通知
        notify_card, notify_layout = make_card("出货通知")

        self._dingtalk_cb = CheckBox("启用钉钉通知")
        self._dingtalk_cb.setChecked(self._settings.get("dingtalk_enabled", False))
        self._dingtalk_cb.stateChanged.connect(self._on_dingtalk_toggled)
        notify_layout.addWidget(self._dingtalk_cb)

        webhook_row = QHBoxLayout()
        webhook_row.addWidget(BodyLabel("Webhook:"))
        self._webhook_input = LineEdit()
        self._webhook_input.setPlaceholderText("钉钉机器人 Webhook 地址")
        self._webhook_input.setText(self._settings.get("dingtalk_webhook", ""))
        self._webhook_input.editingFinished.connect(self._on_webhook_changed)
        webhook_row.addWidget(self._webhook_input)
        notify_layout.addLayout(webhook_row)

        layout.addWidget(notify_card)

        # Steam 用户
        user_card, user_layout = make_card("Steam 用户")

        steam_row = QHBoxLayout()
        steam_row.addWidget(BodyLabel("Steam 路径:"))
        self._steam_path_input = LineEdit()
        self._steam_path_input.setPlaceholderText("Steam 安装目录 (留空自动检测)")
        self._steam_path_input.setText(self._settings.get("steam_path", ""))
        self._steam_path_input.editingFinished.connect(self._on_steam_path_changed)
        steam_row.addWidget(self._steam_path_input)
        steam_browse = PushButton("浏览")
        steam_browse.clicked.connect(self._browse_steam_path)
        steam_row.addWidget(steam_browse)
        user_layout.addLayout(steam_row)

        user_select_row = QHBoxLayout()
        user_select_row.addWidget(BodyLabel("用户:"))
        self._user_combo = ComboBox()
        self._user_combo.currentIndexChanged.connect(self._on_user_changed)
        user_select_row.addWidget(self._user_combo, 1)
        refresh_btn = PushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_users)
        user_select_row.addWidget(refresh_btn)
        user_layout.addLayout(user_select_row)

        layout.addWidget(user_card)

        # 当前存档
        save_card, save_layout = make_card("当前存档")

        self._save_status_label = BodyLabel("未检测")
        save_layout.addWidget(self._save_status_label)

        save_btn_row = QHBoxLayout()
        self._backup_btn = PushButton("备份当前存档")
        self._backup_btn.clicked.connect(self._on_backup)
        self._backup_btn.setEnabled(False)
        save_btn_row.addWidget(self._backup_btn)
        save_btn_row.addStretch()
        save_layout.addLayout(save_btn_row)

        layout.addWidget(save_card)

        # 备份列表
        backup_card, backup_layout = make_card("备份列表")

        backup_dir_row = QHBoxLayout()
        backup_dir_row.addWidget(BodyLabel("备份目录:"))
        self._backup_dir_input = LineEdit()
        self._backup_dir_input.setText(self._settings.get("backup_dir", "data/save_backups"))
        self._backup_dir_input.editingFinished.connect(self._on_backup_dir_changed)
        backup_dir_row.addWidget(self._backup_dir_input)
        backup_dir_browse = PushButton("浏览")
        backup_dir_browse.clicked.connect(self._browse_backup_dir)
        backup_dir_row.addWidget(backup_dir_browse)
        backup_layout.addLayout(backup_dir_row)

        self._backup_list = ListWidget()
        self._backup_list.setMinimumHeight(150)
        backup_layout.addWidget(self._backup_list)

        backup_btn_row = QHBoxLayout()
        restore_btn = PushButton("恢复选中")
        restore_btn.clicked.connect(self._on_restore)
        backup_btn_row.addWidget(restore_btn)
        rename_btn = PushButton("重命名")
        rename_btn.clicked.connect(self._on_rename_backup)
        backup_btn_row.addWidget(rename_btn)
        delete_btn = PushButton("删除")
        delete_btn.clicked.connect(self._on_delete_backup)
        backup_btn_row.addWidget(delete_btn)
        backup_btn_row.addStretch()
        backup_layout.addLayout(backup_btn_row)

        layout.addWidget(backup_card)
        layout.addStretch()

        scroll.setWidget(content)
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)

        self._steam_users = {}
        self._current_steam_id = None
        self._refresh_users()

    # ── 通知 ──

    def _on_dingtalk_toggled(self, state):
        self._settings["dingtalk_enabled"] = bool(state)
        self._save_settings()

    def _on_webhook_changed(self):
        self._settings["dingtalk_webhook"] = self._webhook_input.text()
        self._save_settings()

    # ── Steam 用户 ──

    def _browse_steam_path(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "选择 Steam 目录")
        if d:
            self._steam_path_input.setText(d)
            self._on_steam_path_changed()

    def _on_steam_path_changed(self):
        self._settings["steam_path"] = self._steam_path_input.text()
        self._save_settings()
        self._refresh_users()

    def _refresh_users(self):
        self._steam_users = {}
        self._user_combo.clear()

        steam_path = self._settings.get("steam_path", "")
        if not steam_path:
            for p in [
                r"C:\Program Files (x86)\Steam",
                r"C:\Program Files\Steam",
                os.path.expanduser("~/Library/Application Support/Steam"),
            ]:
                if os.path.isdir(p):
                    steam_path = p
                    break

        if not steam_path or not os.path.isdir(steam_path):
            self._user_combo.addItem("未找到 Steam")
            self._update_save_status()
            return

        vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
        if not os.path.exists(vdf_path):
            self._user_combo.addItem("未找到用户配置")
            self._update_save_status()
            return

        try:
            import re
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for uid, block in re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content):
                props = dict(re.findall(r'"(\w+)"\s+"([^"]*)"', block))
                self._steam_users[uid] = props
                name = props.get("PersonaName", uid)
                recent = " [最近]" if props.get("MostRecent") == "1" else ""
                self._user_combo.addItem(f"{name}{recent}", userData=uid)
        except Exception:
            self._user_combo.addItem("解析用户失败")

        self._update_save_status()

    def _on_user_changed(self, index):
        if index >= 0 and self._user_combo.itemData(index):
            self._current_steam_id = self._user_combo.itemData(index)
        else:
            self._current_steam_id = None
        self._update_save_status()
        self._refresh_backup_list()

    # ── 当前存档 ──

    def _get_save_path(self) -> str:
        if not self._current_steam_id:
            return ""
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(appdata, "Nightreign", self._current_steam_id, "NR0000.sl2")

    def _update_save_status(self):
        save_path = self._get_save_path()
        if not save_path:
            self._save_status_label.setText("请选择 Steam 用户")
            self._backup_btn.setEnabled(False)
            return
        if os.path.exists(save_path):
            size = os.path.getsize(save_path) / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(save_path))
            self._save_status_label.setText(
                f"存档已找到  |  {size:.1f} MB  |  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            self._backup_btn.setEnabled(True)
        else:
            self._save_status_label.setText(f"存档未找到: {save_path}")
            self._backup_btn.setEnabled(False)

    # ── 备份 ──

    def _get_backup_dir(self) -> str:
        base = self._settings.get("backup_dir", "data/save_backups")
        if self._current_steam_id:
            return os.path.join(base, self._current_steam_id)
        return base

    def _on_backup(self):
        save_path = self._get_save_path()
        if not save_path or not os.path.exists(save_path):
            return
        default_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ok = QInputDialog.getText(self, "备份名称", "输入备份名称:", text=default_name)
        if not ok or not name.strip():
            return
        backup_dir = self._get_backup_dir()
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(save_path, os.path.join(backup_dir, f"{name.strip()}.sl2"))
        self._refresh_backup_list()

    def _refresh_backup_list(self):
        self._backup_list.clear()
        backup_dir = self._get_backup_dir()
        if not os.path.isdir(backup_dir):
            return
        files = []
        for f in os.listdir(backup_dir):
            if f.endswith(".sl2"):
                fp = os.path.join(backup_dir, f)
                files.append((f, fp, os.path.getmtime(fp), os.path.getsize(fp)))
        files.sort(key=lambda x: x[2], reverse=True)
        for name, fp, mtime, size in files:
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            size_mb = size / (1024 * 1024)
            item = QListWidgetItem(f"{name[:-4]}  |  {dt}  |  {size_mb:.1f} MB")
            item.setData(Qt.UserRole, fp)
            self._backup_list.addItem(item)

    def _on_restore(self):
        item = self._backup_list.currentItem()
        if not item:
            return
        save_path = self._get_save_path()
        if not save_path:
            return
        w = MessageBox("确认恢复",
            "恢复将覆盖当前存档。\n恢复前会自动备份当前存档。\n确定继续？", self)
        if not w.exec():
            return
        if os.path.exists(save_path):
            auto_name = "auto_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self._get_backup_dir()
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copy2(save_path, os.path.join(backup_dir, f"{auto_name}.sl2"))
        shutil.copy2(item.data(Qt.UserRole), save_path)
        self._update_save_status()
        self._refresh_backup_list()

    def _on_rename_backup(self):
        item = self._backup_list.currentItem()
        if not item:
            return
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)[:-4]
        new_name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=old_name)
        if not ok or not new_name.strip():
            return
        os.rename(old_path, os.path.join(os.path.dirname(old_path), f"{new_name.strip()}.sl2"))
        self._refresh_backup_list()

    def _on_delete_backup(self):
        item = self._backup_list.currentItem()
        if not item:
            return
        w = MessageBox("确认删除", "确定删除该备份？", self)
        if not w.exec():
            return
        os.remove(item.data(Qt.UserRole))
        self._refresh_backup_list()

    def _browse_backup_dir(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if d:
            self._backup_dir_input.setText(d)
            self._on_backup_dir_changed()

    def _on_backup_dir_changed(self):
        self._settings["backup_dir"] = self._backup_dir_input.text()
        self._save_settings()
        self._refresh_backup_list()
