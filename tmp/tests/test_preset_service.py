from __future__ import annotations

from pathlib import Path

from infra.persistence.preset_repository import PresetRepository
from infra.resources.vocabulary_loader import VocabularyLoader
from services.preset_service import PresetService


class TemporaryPresetRepository(PresetRepository):
    def __init__(self, path: Path):
        self.path = path
        self.default_factory = self._build_default_payload


def build_service(tmp_path: Path) -> PresetService:
    vocab_dir = tmp_path / "vocab"
    vocab_dir.mkdir()
    (vocab_dir / "normal.txt").write_text("生命力+1\n", encoding="utf-8")
    (vocab_dir / "normal_special.txt").write_text("提升血量上限\n", encoding="utf-8")
    (vocab_dir / "deepnight_pos.txt").write_text("提升近战攻击力\n", encoding="utf-8")
    (vocab_dir / "deepnight_neg.txt").write_text("持续减少血量\n", encoding="utf-8")
    return PresetService(TemporaryPresetRepository(tmp_path / "presets.json"), VocabularyLoader(vocab_dir, vocab_dir))


def test_default_presets_exist(tmp_path: Path):
    service = build_service(tmp_path)
    presets = service.list_presets()

    assert len(presets) == 1
    assert presets[0].name == "默认预设"
    assert presets[0].normal_relic_affixes == []
    assert presets[0].deepnight_relic_affixes == []
    assert presets[0].blacklist_affixes == []


def test_load_vocabulary_groups(tmp_path: Path):
    service = build_service(tmp_path)

    assert service.load_vocabulary("normal_relic") == ["生命力+1", "提升血量上限"]
    assert service.load_vocabulary("deepnight_relic") == ["提升近战攻击力", "持续减少血量"]
    assert service.load_vocabulary("blacklist") == ["生命力+1", "提升血量上限", "提升近战攻击力", "持续减少血量"]


def test_create_update_toggle_and_delete_preset(tmp_path: Path):
    service = build_service(tmp_path)

    created = service.create_preset("测试预设", ["生命力+1"], ["持续减少血量"], ["提升血量上限"])
    assert created.name == "测试预设"

    updated = service.update_preset(
        created.preset_id,
        name="更新后",
        normal_relic_affixes=["提升血量上限"],
        deepnight_relic_affixes=["持续减少血量"],
        blacklist_affixes=["持续减少血量"],
    )
    assert updated.name == "更新后"
    assert updated.normal_relic_affixes == ["提升血量上限"]
    assert updated.deepnight_relic_affixes == ["持续减少血量"]
    assert updated.blacklist_affixes == ["持续减少血量"]

    toggled = service.toggle_preset_enabled(created.preset_id)
    assert toggled.enabled is False

    service.delete_preset(created.preset_id)
    assert [item.name for item in service.list_presets()] == ["默认预设"]


def test_reorder_presets(tmp_path: Path):
    service = build_service(tmp_path)

    first = service.create_preset("预设A", ["生命力+1"], [], [])
    second = service.create_preset("预设B", ["提升血量上限"], [], [])
    third = service.create_preset("预设C", ["生命力+1"], [], [])

    reordered = service.reorder_presets(first.preset_id, third.preset_id)

    assert [item.preset_id for item in reordered] == ["default_preset", second.preset_id, third.preset_id, first.preset_id]
