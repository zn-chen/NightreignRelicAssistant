"""任务页统计信息面板。"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget


class StatsPanel(QWidget):
    COLORS = {
        "已购买": "#2196F3",
        "已检测": "#2196F3",
        "合格": "#4CAF50",
        "不合格": "#FF9800",
        "已售出": "#F44336",
    }

    def __init__(self, labels: list[str], parent=None):
        super().__init__(parent)
        self._value_labels: dict[str, QLabel] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for label in labels:
            card = CardWidget(self)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(4)

            color = self.COLORS.get(label, "#2196F3")

            title_label = QLabel(label)
            title_label.setStyleSheet(f"color: {color}; font-size: 11pt;")
            card_layout.addWidget(title_label)

            value_label = QLabel("0")
            value_label.setStyleSheet(f"color: {color}; font-size: 20pt; font-weight: bold;")
            card_layout.addWidget(value_label)

            layout.addWidget(card)
            self._value_labels[label] = value_label

    def set_values(self, values: dict[str, int]) -> None:
        for key, label in self._value_labels.items():
            label.setText(str(values.get(key, 0)))
