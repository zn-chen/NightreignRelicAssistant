from __future__ import annotations

import numpy as np

from infra.ocr.engine import RelicEngine
from infra.ocr.ocr import OcrEntry


def _build_positive_entries() -> list[OcrEntry]:
    return [
        OcrEntry(text="1180", score=0.98, x=2.0, y=1.0, height=10.0),
        OcrEntry(text="Nightreign", score=0.95, x=20.0, y=2.0, height=10.0),
        OcrEntry(text="夜王遗物", score=0.99, x=32.0, y=4.0, height=12.0),
        OcrEntry(text="提升物理攻击力", score=0.96, x=40.0, y=30.0, height=10.0),
    ]


class _FakeOcrRunner:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir
        self.calls = 0

    def run(self, image):
        self.calls += 1
        if self.calls == 1:
            return _build_positive_entries()
        return []


def test_vendored_engine_uses_top_left_chinese_title(monkeypatch) -> None:
    monkeypatch.setattr("infra.ocr.engine.OcrRunner", _FakeOcrRunner)
    monkeypatch.setattr("infra.ocr.engine.detect_icon_color", lambda image: "green")
    monkeypatch.setattr("infra.ocr.engine.separate_by_color", lambda image: (image, image))

    engine = RelicEngine(["提升物理攻击力"], [])
    result = engine.recognize(np.zeros((8, 8, 3), dtype=np.uint8))

    assert result.title == "夜王遗物"
    assert "夜王遗物" not in [item.raw for item in result.positive_affixes]
    assert result.matched_positive == ["提升物理攻击力"]


def test_engine_respects_title_switch(monkeypatch) -> None:
    monkeypatch.setattr("infra.ocr.engine.OcrRunner", _FakeOcrRunner)
    monkeypatch.setattr("infra.ocr.engine.detect_icon_color", lambda image: "green")
    monkeypatch.setattr("infra.ocr.engine.separate_by_color", lambda image: (image, image))

    image = np.zeros((8, 8, 3), dtype=np.uint8)
    with_title = RelicEngine(["提升物理攻击力"], []).recognize(
        image,
        expect_title=True,
        detect_icon=True,
    )
    without_title = RelicEngine(["提升物理攻击力"], []).recognize(
        image,
        expect_title=False,
        detect_icon=True,
    )

    assert with_title.title == "夜王遗物"
    assert "夜王遗物" not in [item.raw for item in with_title.positive_affixes]
    assert without_title.title is None
    assert any(item.raw.startswith("夜王遗物") for item in without_title.positive_affixes)