"""OCR 服务抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import OCRResult


class IOCRService(ABC):
    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def recognize_affixes(self, image, profile: str) -> OCRResult:
        raise NotImplementedError
