"""规则引擎抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import OCRResult, RuleContext, RuleEvaluation


class IRuleEngine(ABC):
    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, ocr_result: OCRResult, preset_bundle: dict, context: RuleContext) -> RuleEvaluation:
        raise NotImplementedError
