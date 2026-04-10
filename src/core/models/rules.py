"""规则判定相关模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuleContext:
    mode: str
    scene: str
    relic_version: str | None = None
    require_match_count: int = 2
    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class RuleEvaluation:
    qualified: bool
    reason: str
    matched_affixes: list[str] = field(default_factory=list)
    blocked_affixes: list[str] = field(default_factory=list)
    score: float = 0.0
    error: str | None = None
