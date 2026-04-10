"""设置页面"""

import json
import os
import re
import shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QScrollArea, QInputDialog, QMessageBox, QComboBox,
    QListWidget, QListWidgetItem, QFrame,
)
from PySide6.QtCore import Qt
from nra.ui.widgets.cards import make_card


class SettingsPage(QWidget):
    def __init__(self, settings_path, parent=None):
        super().__init__(parent)
        self._path = settings_path
        self._settings = self._load()
        self._steam_users = {}
        self._steam_id = None
        self._init_ui()
        self._refresh_users()

    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"steam_path": "", "backup_dir": "data/save_backups",
                "dingtalk_enabled": False, "dingtalk_webhook": ""}

    def _save(self):
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(12, 12, 12, 12)
        cl.setSpacing(12)

        # 通知
        nc, nl = make_card("出货通知")
        self._ding_cb = QCheckBox("启用钉钉通知")
        self._ding_cb.setChecked(self._settings.get("dingtalk_enabled", False))
        self._ding_cb.toggled.connect(lambda c: self._set("dingtalk_enabled", c))
        nl.addWidget(self._ding_cb)
        wr = QHBoxLayout()
        wr.addWidget(QLabel("Webhook:"))
        self._webhook = QLineEdit(self._settings.get("dingtalk_webhook", ""))
        self._webhook.setPlaceholderText("钉钉机器人 Webhook 地址")
        self._webhook.editingFinished.connect(lambda: self._set("dingtalk_webhook", self._webhook.text()))
        wr.addWidget(self._webhook)
        nl.addLayout(wr)
        cl.addWidget(nc)

        # Steam
        uc, ul = make_card("Steam 用户")
        sr = QHBoxLayout()
        sr.addWidget(QLabel("Steam 路径:"))
        self._steam = QLineEdit(self._settings.get("steam_path", ""))
        self._steam.setPlaceholderText("留空自动检测")
        self._steam.editingFinished.connect(self._on_steam_changed)
        sr.addWidget(self._steam)
        sb = QPushButton("浏览")
        sb.clicked.connect(lambda: self._browse("steam_path", self._steam, "选择 Steam 目录"))
        sr.addWidget(sb)
        ul.addLayout(sr)
        ur = QHBoxLayout()
        ur.addWidget(QLabel("用户:"))
        self._user_combo = QComboBox()
        self._user_combo.currentIndexChanged.connect(self._on_user_changed)
        ur.addWidget(self._user_combo, 1)
        rb = QPushButton("刷新")
        rb.clicked.connect(self._refresh_users)
        ur.addWidget(rb)
        ul.addLayout(ur)
        cl.addWidget(uc)

        # 存档
        sc, svl = make_card("当前存档")
        self._save_label = QLabel("未检测")
        svl.addWidget(self._save_label)
        br = QHBoxLayout()
        self._bkup_btn = QPushButton("备份当前存档")
        self._bkup_btn.clicked.connect(self._on_backup)
        self._bkup_btn.setEnabled(False)
        br.addWidget(self._bkup_btn)
        br.addStretch()
        svl.addLayout(br)
        cl.addWidget(sc)

        # 备份列表
        bc, bl = make_card("备份列表")
        dr = QHBoxLayout()
        dr.addWidget(QLabel("备份目录:"))
        self._bdir = QLineEdit(self._settings.get("backup_dir", "data/save_backups"))
        self._bdir.editingFinished.connect(lambda: (self._set("backup_dir", self._bdir.text()), self._refresh_backups()))
        dr.addWidget(self._bdir)
        db = QPushButton("浏览")
        db.clicked.connect(lambda: (self._browse("backup_dir", self._bdir, "选择备份目录"), self._refresh_backups()))
        dr.addWidget(db)
        bl.addLayout(dr)
        self._bklist = QListWidget()
        self._bklist.setMinimumHeight(150)
        bl.addWidget(self._bklist)
        bbr = QHBoxLayout()
        for text, handler in [("恢复", self._on_restore), ("重命名", self._on_rename), ("删除", self._on_del_backup)]:
            b = QPushButton(text)
            b.clicked.connect(handler)
            bbr.addWidget(b)
        bbr.addStretch()
        bl.addLayout(bbr)
        cl.addWidget(bc)

        cl.addStretch()
        scroll.setWidget(content)
        page = QVBoxLayout(self)
        page.setContentsMargins(0, 0, 0, 0)
        page.addWidget(scroll)

    def _set(self, key, val):
        self._settings[key] = val
        self._save()

    def _browse(self, key, line_edit, title):
        d = QFileDialog.getExistingDirectory(self, title)
        if d:
            line_edit.setText(d)
            self._set(key, d)

    def _on_steam_changed(self):
        self._set("steam_path", self._steam.text())
        self._refresh_users()

    def _refresh_users(self):
        self._steam_users = {}
        self._user_combo.clear()
        sp = self._settings.get("steam_path", "")
        if not sp:
            for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam",
                       os.path.expanduser("~/Library/Application Support/Steam")]:
                if os.path.isdir(p):
                    sp = p
                    break
        if not sp or not os.path.isdir(sp):
            self._user_combo.addItem("未找到 Steam")
            self._update_save()
            return
        vdf = os.path.join(sp, "config", "loginusers.vdf")
        if not os.path.exists(vdf):
            self._user_combo.addItem("未找到用户配置")
            self._update_save()
            return
        try:
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for uid, block in re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content):
                props = dict(re.findall(r'"(\w+)"\s+"([^"]*)"', block))
                self._steam_users[uid] = props
                name = props.get("PersonaName", uid)
                tag = " [最近]" if props.get("MostRecent") == "1" else ""
                self._user_combo.addItem(f"{name}{tag}", uid)
        except Exception:
            self._user_combo.addItem("解析失败")
        self._update_save()

    def _on_user_changed(self, i):
        self._steam_id = self._user_combo.itemData(i) if i >= 0 else None
        self._update_save()
        self._refresh_backups()

    def _save_path(self):
        if not self._steam_id:
            return ""
        return os.path.join(os.environ.get("APPDATA", ""), "Nightreign", self._steam_id, "NR0000.sl2")

    def _update_save(self):
        p = self._save_path()
        if not p:
            self._save_label.setText("请选择用户")
            self._bkup_btn.setEnabled(False)
        elif os.path.exists(p):
            s = os.path.getsize(p) / 1048576
            t = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
            self._save_label.setText(f"已找到 | {s:.1f} MB | {t}")
            self._bkup_btn.setEnabled(True)
        else:
            self._save_label.setText(f"未找到: {p}")
            self._bkup_btn.setEnabled(False)

    def _backup_dir(self):
        base = self._settings.get("backup_dir", "data/save_backups")
        return os.path.join(base, self._steam_id) if self._steam_id else base

    def _on_backup(self):
        p = self._save_path()
        if not p or not os.path.exists(p):
            return
        name, ok = QInputDialog.getText(self, "备份", "名称:", text=datetime.now().strftime("%Y%m%d_%H%M%S"))
        if not ok or not name.strip():
            return
        d = self._backup_dir()
        os.makedirs(d, exist_ok=True)
        shutil.copy2(p, os.path.join(d, f"{name.strip()}.sl2"))
        self._refresh_backups()

    def _refresh_backups(self):
        self._bklist.clear()
        d = self._backup_dir()
        if not os.path.isdir(d):
            return
        files = [(f, os.path.join(d, f)) for f in os.listdir(d) if f.endswith(".sl2")]
        files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
        for name, fp in files:
            t = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
            s = os.path.getsize(fp) / 1048576
            item = QListWidgetItem(f"{name[:-4]} | {t} | {s:.1f} MB")
            item.setData(Qt.UserRole, fp)
            self._bklist.addItem(item)

    def _on_restore(self):
        item = self._bklist.currentItem()
        if not item:
            return
        p = self._save_path()
        if not p:
            return
        if QMessageBox.question(self, "确认", "恢复前会自动备份。继续？") != QMessageBox.Yes:
            return
        if os.path.exists(p):
            d = self._backup_dir()
            os.makedirs(d, exist_ok=True)
            shutil.copy2(p, os.path.join(d, f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sl2"))
        shutil.copy2(item.data(Qt.UserRole), p)
        self._update_save()
        self._refresh_backups()

    def _on_rename(self):
        item = self._bklist.currentItem()
        if not item:
            return
        old = item.data(Qt.UserRole)
        name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=os.path.basename(old)[:-4])
        if ok and name.strip():
            os.rename(old, os.path.join(os.path.dirname(old), f"{name.strip()}.sl2"))
            self._refresh_backups()

    def _on_del_backup(self):
        item = self._bklist.currentItem()
        if not item:
            return
        if QMessageBox.question(self, "确认", "删除该备份？") == QMessageBox.Yes:
            os.remove(item.data(Qt.UserRole))
            self._refresh_backups()
