"""应用内共用的 OCR 结果模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AffixRecognition:
    raw_text: str
    normalized_text: str
    confidence: float
    source_line: int | None = None
    source_region: str | None = None


@dataclass(slots=True)
class OCRResult:
    success: bool
    affixes: list[AffixRecognition] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0
    error: str | None = None
