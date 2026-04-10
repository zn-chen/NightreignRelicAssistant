"""OCR 封装 — RapidOCR 调用与结果排序"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from rapidocr import RapidOCR


@dataclass
class OcrEntry:
    """单条 OCR 识别结果"""

    text: str
    score: float
    x: float
    y: float
    height: float


class OcrRunner:
    """RapidOCR 封装，可自定义模型路径或使用默认模型。"""

    def __init__(self, model_dir: Optional[str] = None) -> None:
        """
        Args:
            model_dir: ONNX 模型目录，需包含
                       ch_PP-OCRv4_det_infer.onnx,
                       ch_ppocr_mobile_v2.0_cls_infer.onnx,
                       ch_PP-OCRv4_rec_infer.onnx
                       为 None 时使用 RapidOCR 默认模型。
        """

        if model_dir is not None:
            import os

            self._engine = RapidOCR(
                params={
                    "Det.model_path": os.path.join(model_dir, "ch_PP-OCRv4_det_infer.onnx"),
                    "Cls.model_path": os.path.join(model_dir, "ch_ppocr_mobile_v2.0_cls_infer.onnx"),
                    "Rec.model_path": os.path.join(model_dir, "ch_PP-OCRv4_rec_infer.onnx"),
                }
            )
        else:
            self._engine = RapidOCR()

    def run(self, image: np.ndarray) -> list[OcrEntry]:
        """对图像执行 OCR，返回按 Y 坐标排序的结果列表。"""

        result = self._engine(image, use_det=True, use_cls=False)
        if not result or not result.txts:
            return []

        entries = []
        for i, (text, score) in enumerate(zip(result.txts, result.scores)):
            text = text.strip()
            if not text:
                continue
            box = result.boxes[i] if result.boxes is not None else None
            if box is not None:
                x_values = [float(point[0]) for point in box]
                y_values = [float(point[1]) for point in box]
                x_pos = min(x_values)
                y_pos = min(y_values)
                height = max(y_values) - y_pos
            else:
                x_pos = float(i * 100)
                y_pos = float(i * 100)
                height = 0.0
            entries.append(OcrEntry(text=text, score=score, x=x_pos, y=y_pos, height=height))

        entries.sort(key=lambda e: e.y)
        return entries