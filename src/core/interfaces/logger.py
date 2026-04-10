"""日志输出抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ILogSink(ABC):
    @abstractmethod
    def info(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str) -> None:
        raise NotImplementedError
