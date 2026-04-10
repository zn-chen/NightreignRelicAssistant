"""识别历史记录相关模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RelicHistoryRecord:
    record_id: str
    created_at: str
    source: str
    index: int = 0
    affixes: list[dict] = field(default_factory=list)
    extra: dict = field(default_factory=dict)
