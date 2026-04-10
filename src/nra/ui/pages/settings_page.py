"""设置页面"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog,
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
        return {"vocab_dir": "data", "data_dir": "data"}

    def _save(self):
        os.makedirs(os.path.dirname(self._settings_path) or ".", exist_ok=True)
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(12)

        # 路径配置
        paths_card, paths_layout = make_card("路径配置")

        vocab_layout = QHBoxLayout()
        vocab_layout.addWidget(QLabel("词条库目录:"))
        self._vocab_dir_input = QLineEdit(self._settings.get("vocab_dir", "data"))
        self._vocab_dir_input.editingFinished.connect(self._on_vocab_dir_changed)
        vocab_layout.addWidget(self._vocab_dir_input)
        vocab_browse = QPushButton("浏览")
        vocab_browse.clicked.connect(self._browse_vocab_dir)
        vocab_layout.addWidget(vocab_browse)
        paths_layout.addLayout(vocab_layout)

        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("数据存储目录:"))
        self._data_dir_input = QLineEdit(self._settings.get("data_dir", "data"))
        self._data_dir_input.editingFinished.connect(self._on_data_dir_changed)
        data_layout.addWidget(self._data_dir_input)
        data_browse = QPushButton("浏览")
        data_browse.clicked.connect(self._browse_data_dir)
        data_layout.addWidget(data_browse)
        paths_layout.addLayout(data_layout)

        layout.addWidget(paths_card)
        layout.addStretch()

    def _browse_vocab_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择词条库目录")
        if d:
            self._vocab_dir_input.setText(d)
            self._on_vocab_dir_changed()

    def _browse_data_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择数据存储目录")
        if d:
            self._data_dir_input.setText(d)
            self._on_data_dir_changed()

    def _on_vocab_dir_changed(self):
        self._settings["vocab_dir"] = self._vocab_dir_input.text()
        self._save()

    def _on_data_dir_changed(self):
        self._settings["data_dir"] = self._data_dir_input.text()
        self._save()
