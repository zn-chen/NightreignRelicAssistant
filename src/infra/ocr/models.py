"""识别结果数据模型"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AffixMatch:
    """单条词条的匹配结果"""

    raw: str
    matched: str | None
    score: float

    @property
    def is_matched(self) -> bool:
        return self.matched is not None


@dataclass
class RelicResult:
    """遗物识别的完整结果"""

    title: str | None = None
    icon_color: str = "unknown"
    positive_affixes: list[AffixMatch] = field(default_factory=list)
    negative_affixes: list[AffixMatch] = field(default_factory=list)

    @property
    def matched_positive(self) -> list[str]:
        """成功匹配的正面词条名称列表"""

        return [a.matched for a in self.positive_affixes if a.is_matched]

    @property
    def matched_negative(self) -> list[str]:
        """成功匹配的负面词条名称列表"""

        return [a.matched for a in self.negative_affixes if a.is_matched]