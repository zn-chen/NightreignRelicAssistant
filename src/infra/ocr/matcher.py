"""模糊匹配 — 词条匹配与匹配驱动合并"""

from __future__ import annotations

from typing import Sequence

from rapidfuzz import fuzz

from infra.ocr.models import AffixMatch
from infra.ocr.ocr import OcrEntry


def match_affix(
    text: str,
    vocabulary: Sequence[str],
    threshold: float = 65.0,
) -> AffixMatch:
    """对单条文本在词条库中做模糊匹配。"""

    best_match = None
    best_score = 0.0

    for vocab in vocabulary:
        score = fuzz.ratio(text, vocab)
        if score > best_score:
            best_score = score
            best_match = vocab

    if best_score >= threshold:
        return AffixMatch(raw=text, matched=best_match, score=best_score)
    return AffixMatch(raw=text, matched=None, score=best_score)


def match_and_merge(
    entries: Sequence[OcrEntry],
    vocabulary: Sequence[str],
    threshold: float = 65.0,
) -> list[AffixMatch]:
    """匹配驱动合并 — 先匹配，匹配不上再尝试与下一行合并。

    逻辑:
    1. 当前行单独匹配词条库
    2. 如果匹配分数 >= threshold → 直接采纳
    3. 如果匹配分数低 → 尝试拼接下一行再匹配
    4. 取单独 vs 合并中分数更高的结果
    """

    if not entries:
        return []

    texts = [e.text for e in entries]
    results = []
    i = 0

    while i < len(texts):
        current = texts[i]
        single = match_affix(current, vocabulary, threshold)

        merged = None
        if i + 1 < len(texts):
            merged_text = current + texts[i + 1]
            merged = match_affix(merged_text, vocabulary, threshold)

        if merged and merged.is_matched and merged.score > single.score:
            results.append(merged)
            i += 2
        elif single.is_matched:
            results.append(single)
            i += 1
        else:
            results.append(single)
            i += 1

    return results