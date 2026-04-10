"""仓库流程后台线程。"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal


class RepoWorker(QThread):
    log_signal = Signal(str, str)
    stats_signal = Signal(dict)
    finished_signal = Signal()

    def __init__(self, service, *, mode: str, cleaning_mode: str, max_relics: int, allow_operate_favorited: bool, require_double: bool, parent=None):
        super().__init__(parent)
        self.service = service
        self.mode = mode
        self.cleaning_mode = cleaning_mode
        self.max_relics = max_relics
        self.allow_operate_favorited = allow_operate_favorited
        self.require_double = require_double

    def run(self) -> None:
        try:
            self.service.start(
                mode=self.mode,
                cleaning_mode=self.cleaning_mode,
                max_relics=self.max_relics,
                allow_operate_favorited=self.allow_operate_favorited,
                require_double=self.require_double,
                log_callback=self.log_signal.emit,
                stats_callback=self.stats_signal.emit,
            )
        finally:
            self.finished_signal.emit()
