"""商店流程后台线程。"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal


class ShopWorker(QThread):
    log_signal = Signal(str, str)
    stats_signal = Signal(dict)
    finished_signal = Signal()

    def __init__(self, service, *, mode: str, version: str, stop_currency: int, require_double: bool, sl_mode_enabled: bool, sl_target: int, parent=None):
        super().__init__(parent)
        self.service = service
        self.mode = mode
        self.version = version
        self.stop_currency = stop_currency
        self.require_double = require_double
        self.sl_mode_enabled = sl_mode_enabled
        self.sl_target = sl_target

    def run(self) -> None:
        try:
            self.service.start(
                mode=self.mode,
                version=self.version,
                stop_currency=self.stop_currency,
                require_double=self.require_double,
                sl_mode_enabled=self.sl_mode_enabled,
                sl_target=self.sl_target,
                log_callback=self.log_signal.emit,
                stats_callback=self.stats_signal.emit,
            )
        finally:
            self.finished_signal.emit()
