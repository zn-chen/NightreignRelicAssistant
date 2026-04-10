"""核心可插拔接口集合。"""

from .automation import IAutomationGateway
from .detector import IRelicStateDetector
from .logger import ILogSink
from .ocr import IOCRService
from .repository import IJsonRepository
from .rule_engine import IRuleEngine

__all__ = [
    "IAutomationGateway",
    "IRelicStateDetector",
    "ILogSink",
    "IOCRService",
    "IJsonRepository",
    "IRuleEngine",
]
