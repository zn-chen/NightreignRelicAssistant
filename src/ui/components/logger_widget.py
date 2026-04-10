"""任务页使用的富文本日志组件。"""

from __future__ import annotations

import html
from datetime import datetime

from PySide6.QtWidgets import QTextEdit
from qfluentwidgets import isDarkTheme


class LoggerWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self._update_stylesheet()

    def _update_stylesheet(self) -> None:
        # 每次写日志前都重新应用样式，保证主题切换后日志框外观能即时跟上。
        if isDarkTheme():
            stylesheet = """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 11pt;
                    line-height: 1.5;
                }
            """
        else:
            stylesheet = """
                QTextEdit {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #e8e8e8;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 11pt;
                    line-height: 1.5;
                }
            """
        self.setStyleSheet(stylesheet)

    def log(self, level: str, message: str | None = None) -> None:
        if message is None:
            message = level
            level = "INFO"

        self._update_stylesheet()

        colors = {
            "INFO": "#0066cc",
            "SUCCESS": "#27ae60",
            "WARNING": "#f39c12",
            "ERROR": "#e74c3c",
            "DEBUG": "#95a5a6",
        }
        # 日志内容做 HTML 转义后再写入富文本，避免用户文本破坏显示结构。
        safe_message = html.escape(message)
        text_color = "#e0e0e0" if isDarkTheme() else "#333333"
        color = colors.get(level.upper(), "#333333")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(
            f'<span style="color: {color}; font-weight: 500;">[{timestamp}]</span> '
            f'<span style="color: {color};">[{level.upper()}]</span> '
            f'<span style="color: {text_color};">{safe_message}</span>'
        )

    def clear_log(self) -> None:
        self.clear()
