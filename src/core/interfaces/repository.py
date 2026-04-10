"""仓储访问抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IJsonRepository(ABC):
    @abstractmethod
    def load(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def save(self, payload: dict[str, Any]) -> None:
        raise NotImplementedError
