"""基于 Nightreign 遗物引擎的 OCR 服务实现。"""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from core.interfaces import IOCRService
from core.models import AffixRecognition, OCRResult
from infra.resources.vocabulary_loader import VocabularyLoader
from infra.system.paths import get_ocr_models_dir
from infra.ocr import RelicEngine


POSITIVE_VOCABULARY_FILES = ["normal.txt", "normal_special.txt", "deepnight_pos.txt"]
NEGATIVE_VOCABULARY_FILES = ["deepnight_neg.txt"]
OCR_PROFILE_OPTIONS = {
    "repo_affixes": {"expect_title": True, "detect_icon": True},
    "shop_affixes": {"expect_title": False, "detect_icon": False},
}


class NightreignOCRService(IOCRService):
    def __init__(
        self,
        vocabulary_loader: VocabularyLoader,
        *,
        model_dir: Path | None = None,
        match_threshold: float = 65.0,
    ) -> None:
        self.vocabulary_loader = vocabulary_loader
        self.model_dir = model_dir
        self.match_threshold = match_threshold
        self._engine: RelicEngine | None = None

    def initialize(self) -> None:
        if self._engine is not None:
            return

        # 启动阶段先把词库装入内存，避免每次识别都重复读文件。
        positive_vocabulary = self.vocabulary_loader.load(POSITIVE_VOCABULARY_FILES)
        negative_vocabulary = self.vocabulary_loader.load(NEGATIVE_VOCABULARY_FILES)
        if not positive_vocabulary and not negative_vocabulary:
            raise RuntimeError("OCR vocabularies are empty")

        resolved_model_dir = self._resolve_model_dir()
        self._engine = RelicEngine(
            pos_vocabulary=positive_vocabulary,
            neg_vocabulary=negative_vocabulary,
            model_dir=str(resolved_model_dir) if resolved_model_dir is not None else None,
            match_threshold=self.match_threshold,
        )

    def is_ready(self) -> bool:
        return self._engine is not None

    def recognize_affixes(self, image, profile: str) -> OCRResult:
        if self._engine is None:
            return OCRResult(success=False, error="OCR 服务尚未初始化")
        if image is None:
            return OCRResult(success=False, error="未提供可识别的图像")

        try:
            prepared_image = self._to_bgr_image(image)
        except Exception as exc:
            return OCRResult(success=False, error=f"图像预处理失败: {exc}")

        started = perf_counter()

        # 不同识别场景复用同一引擎，但通过 profile 控制是否识别标题和图标颜色。
        profile_options = OCR_PROFILE_OPTIONS.get(profile, {"expect_title": False, "detect_icon": False})
        try:
            result = self._engine.recognize(
                prepared_image,
                expect_title=profile_options["expect_title"],
                detect_icon=profile_options["detect_icon"],
            )
        except Exception as exc:
            return OCRResult(
                success=False,
                elapsed_ms=(perf_counter() - started) * 1000,
                error=f"OCR 识别失败: {exc}",
            )

        elapsed_ms = (perf_counter() - started) * 1000
        affixes: list[AffixRecognition] = []
        raw_lines: list[str] = []

        # 标题单独保留在 raw_lines 里，便于调试时还原完整 OCR 输出。
        if result.title:
            raw_lines.append(result.title)

        for index, affix in enumerate(result.positive_affixes, start=1):
            raw_lines.append(affix.raw)
            affixes.append(
                AffixRecognition(
                    raw_text=affix.raw,
                    normalized_text=affix.matched or affix.raw,
                    confidence=float(affix.score),
                    source_line=index,
                    source_region=f"{profile}:positive",
                )
            )

        for index, affix in enumerate(result.negative_affixes, start=1):
            raw_lines.append(affix.raw)
            affixes.append(
                AffixRecognition(
                    raw_text=affix.raw,
                    normalized_text=affix.matched or affix.raw,
                    confidence=float(affix.score),
                    source_line=index,
                    source_region=f"{profile}:negative",
                )
            )

        if not raw_lines and not affixes:
            return OCRResult(success=False, raw_lines=[], elapsed_ms=elapsed_ms, error="未识别到任何词条")

        return OCRResult(success=True, affixes=affixes, raw_lines=raw_lines, elapsed_ms=elapsed_ms)

    def _resolve_model_dir(self) -> Path | None:
        if self.model_dir is not None:
            if not self.model_dir.exists():
                raise RuntimeError(f"OCR model directory not found: {self.model_dir}")
            return self.model_dir
        return get_ocr_models_dir()

    @staticmethod
    def _to_bgr_image(image) -> np.ndarray:
        if isinstance(image, np.ndarray):
            return NightreignOCRService._normalize_ndarray(image)

        array = np.asarray(image)
        if array.size == 0:
            raise ValueError("empty image")

        if image.__class__.__module__.startswith("PIL."):
            return NightreignOCRService._convert_rgb_like(array)
        return NightreignOCRService._normalize_ndarray(array)

    @staticmethod
    def _normalize_ndarray(array: np.ndarray) -> np.ndarray:
        if array.ndim == 2:
            return cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)
        if array.ndim != 3:
            raise ValueError(f"unsupported image shape: {array.shape}")
        if array.shape[2] == 4:
            return cv2.cvtColor(array, cv2.COLOR_BGRA2BGR)
        if array.shape[2] == 3:
            return np.ascontiguousarray(array)
        raise ValueError(f"unsupported image shape: {array.shape}")

    @staticmethod
    def _convert_rgb_like(array: np.ndarray) -> np.ndarray:
        if array.ndim == 2:
            return cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)
        if array.ndim != 3:
            raise ValueError(f"unsupported image shape: {array.shape}")
        if array.shape[2] == 4:
            return cv2.cvtColor(array, cv2.COLOR_RGBA2BGR)
        if array.shape[2] == 3:
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        raise ValueError(f"unsupported image shape: {array.shape}")