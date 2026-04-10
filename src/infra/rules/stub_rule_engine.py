"""安全占位的规则引擎实现。"""

from __future__ import annotations

from core.interfaces import IRuleEngine
from core.models import OCRResult, RuleContext, RuleEvaluation


class StubRuleEngine(IRuleEngine):
    def is_ready(self) -> bool:
        return False

    def evaluate(self, ocr_result: OCRResult, preset_bundle: dict, context: RuleContext) -> RuleEvaluation:
        _ = ocr_result, preset_bundle, context
        return RuleEvaluation(qualified=False, reason="rule_engine_missing", error="未配置规则引擎")
