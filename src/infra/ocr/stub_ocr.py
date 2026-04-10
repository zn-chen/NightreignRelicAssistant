"""在真实 OCR 接入前使用的占位实现。"""

from __future__ import annotations

from core.interfaces import IOCRService
from core.models import OCRResult


class StubOCRService(IOCRService):
    def __init__(self):
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def is_ready(self) -> bool:
        return self.initialized

    def recognize_affixes(self, image, profile: str) -> OCRResult:
        return OCRResult(success=False, error="未配置 OCR 适配器")

