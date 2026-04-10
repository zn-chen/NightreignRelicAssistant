"""应用界面使用的稳定下拉框封装。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QListView


class StableComboBox(QComboBox):
    """Qt combo box with a restrained style and qfluent-compatible addItem signature."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 统一切到 Qt 原生下拉框，规避当前环境下 qfluentwidgets 下拉阴影伪影问题。
        self.setCursor(Qt.PointingHandCursor)
        self.setView(QListView(self))
        self.setMaxVisibleItems(12)
        self.setMinimumHeight(33)
        self._apply_stylesheet()

    def addItem(self, text, icon=None, userData=None):
        if icon is None:
            super().addItem(text, userData)
            return

        if not isinstance(icon, QIcon):
            icon = QIcon(icon)
        super().addItem(icon, text, userData)

    def addItems(self, texts):
        for text in texts:
            self.addItem(text)

    def showPopup(self) -> None:
        # 打开下拉前把弹层宽度至少撑到宿主宽度，避免文字被截断。
        self.view().setMinimumWidth(self.width())
        super().showPopup()

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d8d8d8;
                border-radius: 6px;
                padding: 0 28px 0 10px;
                color: #111111;
            }
            QComboBox:hover {
                border-color: #c6c6c6;
            }
            QComboBox:focus {
                border-color: #009faa;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border: none;
                background: transparent;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #111111;
                border: 1px solid #d8d8d8;
                selection-background-color: #f3f3f3;
                selection-color: #111111;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 4px 8px;
            }
            """
        )