"""标题候选选择逻辑。"""

from __future__ import annotations

import re
from collections.abc import Sequence

from infra.ocr.ocr import OcrEntry


CHINESE_TEXT_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def contains_chinese(text: str) -> bool:
    return bool(CHINESE_TEXT_RE.search(text))


def find_title_entry(entries: Sequence[OcrEntry]) -> tuple[int, OcrEntry] | None:
    candidates = [
        (index, entry)
        for index, entry in enumerate(entries)
        if contains_chinese(entry.text)
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item[1].y, item[1].x))