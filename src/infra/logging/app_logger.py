"""支持文件落盘和界面订阅的应用日志器。"""

from __future__ import annotations

import logging
from pathlib import Path

from infra.system.paths import get_logs_dir


class AppLogger:
    def __init__(self, name: str = "nightreign_relic_assistant"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        self.subscribers = []

        # 文件日志和界面广播共用同一套 logger，避免不同输出源格式漂移。
        self._configure_handlers(get_logs_dir() / "app.log")

    def _configure_handlers(self, log_path: Path) -> None:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        # 当前保留最稳定的文件落盘链路，界面更新由订阅回调单独承担。
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def subscribe(self, callback) -> None:
        self.subscribers.append(callback)

    def _emit(self, level: str, message: str) -> None:
        getattr(self.logger, level.lower())(message)

        # 每条日志同步广播给订阅页面，让 UI 不必主动轮询日志文件。
        for callback in self.subscribers:
            callback(level.upper(), message)

    def info(self, message: str) -> None:
        self._emit("info", message)

    def warning(self, message: str) -> None:
        self._emit("warning", message)

    def error(self, message: str) -> None:
        self._emit("error", message)
