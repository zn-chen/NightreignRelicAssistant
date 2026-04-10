"""遗物识别引擎 — 图片进、结构化数据出"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from infra.ocr.color import detect_icon_color, separate_by_color
from infra.ocr.matcher import match_and_merge
from infra.ocr.models import RelicResult
from infra.ocr.ocr import OcrRunner
from infra.ocr.title import find_title_entry


class RelicEngine:
    """遗物识别引擎。

    用法::

        engine = RelicEngine(
            pos_vocabulary=["生命力+1", "力量+2", ...],
            neg_vocabulary=["受到攻击时蓄积毒", ...],
        )
        result = engine.recognize(image)
        print(result.title, result.icon_color)
        print(result.matched_positive)
        print(result.matched_negative)
    """

    def __init__(
        self,
        pos_vocabulary: Sequence[str],
        neg_vocabulary: Sequence[str],
        model_dir: Optional[str] = None,
        match_threshold: float = 65.0,
    ) -> None:
        """
        Args:
            pos_vocabulary: 正面词条库
            neg_vocabulary: 负面词条库
            model_dir: ONNX 模型目录，为 None 时使用默认模型
            match_threshold: 模糊匹配阈值 (0-100)
        """
        self._pos_vocab = list(pos_vocabulary)
        self._neg_vocab = list(neg_vocabulary)
        self._threshold = match_threshold
        self._ocr = OcrRunner(model_dir)

    def recognize(
        self,
        image: np.ndarray,
        *,
        expect_title: bool = True,
        detect_icon: bool = True,
    ) -> RelicResult:
        """识别一张遗物区域截图。

        Args:
            image: BGR 格式的遗物区域截图 (numpy array)

            expect_title: 是否将最左上中文识别结果视为标题并从正面词条中移除
            detect_icon: 是否检测图标颜色

        Returns:
            RelicResult 包含标题、图标颜色、正面词条、负面词条
        """
        result = RelicResult()

        result.icon_color = detect_icon_color(image) if detect_icon else "unknown"

        pos_mask, neg_mask = separate_by_color(image)

        pos_entries = self._ocr.run(pos_mask)
        if pos_entries:
            affix_entries = list(pos_entries)
            if expect_title:
                title_candidate = find_title_entry(pos_entries)
                if title_candidate is not None:
                    title_index, title_entry = title_candidate
                    result.title = title_entry.text
                    affix_entries = [
                        entry for index, entry in enumerate(pos_entries) if index != title_index
                    ]
            result.positive_affixes = match_and_merge(
                affix_entries, self._pos_vocab, self._threshold
            )

        neg_entries = self._ocr.run(neg_mask)
        if neg_entries:
            result.negative_affixes = match_and_merge(
                neg_entries, self._neg_vocab, self._threshold
            )

        return result