"""自动化网关抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IAutomationGateway(ABC):
    @abstractmethod
    def focus_game(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def capture(self, region_name: str | None = None):
        raise NotImplementedError

    @abstractmethod
    def press(self, key: str, duration: float = 0.05) -> None:
        raise NotImplementedError

    @abstractmethod
    def click_anchor(self, anchor_name: str) -> bool:
        raise NotImplementedError
