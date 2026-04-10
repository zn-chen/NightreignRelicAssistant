"""OCR 初始化后台线程。"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal


class OCRInitWorker(QThread):
    succeeded = Signal()
    failed = Signal(str)

    def __init__(self, ocr_service, parent=None):
        super().__init__(parent)
        self.ocr_service = ocr_service

    def run(self) -> None:
        try:
            self.ocr_service.initialize()
            self.succeeded.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
