"""遗物状态检测器抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IRelicStateDetector(ABC):
    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def detect_relic_state(self, screenshot) -> str:
        raise NotImplementedError
