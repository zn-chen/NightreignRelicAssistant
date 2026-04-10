"""核心数据模型集合。"""

from .history import RelicHistoryRecord
from .ocr import AffixRecognition, OCRResult
from .preset import PresetRecord, PresetStore
from .rules import RuleContext, RuleEvaluation
from .runtime import AppSettings, TaskStats
from .workflow import ActionDecision, TaskRuntimeState

__all__ = [
    "AffixRecognition",
    "OCRResult",
    "RelicHistoryRecord",
    "PresetRecord",
    "PresetStore",
    "RuleContext",
    "RuleEvaluation",
    "AppSettings",
    "ActionDecision",
    "TaskRuntimeState",
    "TaskStats",
]
