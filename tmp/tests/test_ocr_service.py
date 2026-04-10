from __future__ import annotations

from pathlib import Path

import numpy as np

from infra.ocr.models import AffixMatch, RelicResult
from infra.ocr.relic_ocr_service import NightreignOCRService


class FakeVocabularyLoader:
    def load(self, filenames: list[str]) -> list[str]:
        mapping = {
            "normal.txt": ["生命力+1"],
            "normal_special.txt": ["力量+2"],
            "deepnight_pos.txt": ["深夜攻击提升"],
            "deepnight_neg.txt": ["持续掉血"],
        }
        values: list[str] = []
        for filename in filenames:
            values.extend(mapping.get(filename, []))
        return values


def test_initialize_builds_engine_with_expected_vocabularies(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakeEngine:
        def __init__(self, pos_vocabulary, neg_vocabulary, model_dir=None, match_threshold=65.0):
            captured["pos_vocabulary"] = list(pos_vocabulary)
            captured["neg_vocabulary"] = list(neg_vocabulary)
            captured["model_dir"] = model_dir
            captured["match_threshold"] = match_threshold

    monkeypatch.setattr(
        "infra.ocr.relic_ocr_service.RelicEngine",
        FakeEngine,
    )
    monkeypatch.setattr(
        "infra.ocr.relic_ocr_service.get_ocr_models_dir",
        lambda: tmp_path,
    )

    service = NightreignOCRService(FakeVocabularyLoader(), match_threshold=72.5)
    service.initialize()

    assert captured == {
        "pos_vocabulary": ["生命力+1", "力量+2", "深夜攻击提升"],
        "neg_vocabulary": ["持续掉血"],
        "model_dir": str(tmp_path),
        "match_threshold": 72.5,
    }
    assert service.is_ready() is True


def test_recognize_affixes_maps_engine_output() -> None:
    calls: dict[str, bool] = {}

    class FakeEngine:
        def recognize(self, image: np.ndarray, *, expect_title: bool, detect_icon: bool) -> RelicResult:
            assert image.shape == (12, 8, 3)
            calls["expect_title"] = expect_title
            calls["detect_icon"] = detect_icon
            return RelicResult(
                title="夜王遗物",
                positive_affixes=[AffixMatch(raw="生命力十1", matched="生命力+1", score=91.2)],
                negative_affixes=[AffixMatch(raw="持续掉皿", matched="持续掉血", score=88.5)],
            )

    service = NightreignOCRService(FakeVocabularyLoader())
    service._engine = FakeEngine()

    result = service.recognize_affixes(np.zeros((12, 8, 3), dtype=np.uint8), "shop_affixes")

    assert result.success is True
    assert calls == {"expect_title": False, "detect_icon": False}
    assert result.raw_lines == ["夜王遗物", "生命力十1", "持续掉皿"]
    assert [item.normalized_text for item in result.affixes] == ["生命力+1", "持续掉血"]
    assert [item.source_region for item in result.affixes] == ["shop_affixes:positive", "shop_affixes:negative"]


def test_recognize_affixes_uses_full_card_profile_for_repo() -> None:
    calls: dict[str, bool] = {}

    class FakeEngine:
        def recognize(self, image: np.ndarray, *, expect_title: bool, detect_icon: bool) -> RelicResult:
            calls["expect_title"] = expect_title
            calls["detect_icon"] = detect_icon
            return RelicResult()

    service = NightreignOCRService(FakeVocabularyLoader())
    service._engine = FakeEngine()

    result = service.recognize_affixes(np.zeros((12, 8, 3), dtype=np.uint8), "repo_affixes")

    assert calls == {"expect_title": True, "detect_icon": True}
    assert result.success is False
    assert result.error == "未识别到任何词条"