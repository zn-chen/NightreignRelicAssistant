"""Tests for PresetManager."""

import os
import pytest
from nra.models.preset_manager import PresetManager


@pytest.fixture
def tmp_filepath(tmp_path):
    return str(tmp_path / "presets.json")


@pytest.fixture
def pm(tmp_filepath):
    return PresetManager(tmp_filepath)


class TestInitialState:
    def test_empty_builds(self, pm):
        assert pm.builds == []

    def test_empty_common_groups(self, pm):
        assert pm.common_groups == []


class TestSaveAndLoad:
    def test_round_trip_empty(self, tmp_filepath):
        pm = PresetManager(tmp_filepath)
        pm.save()
        pm2 = PresetManager(tmp_filepath)
        assert pm2.builds == []
        assert pm2.common_groups == []

    def test_round_trip_with_data(self, tmp_filepath):
        pm = PresetManager(tmp_filepath)
        pm.create_build("Test Build")
        pm.create_common_group("Common A")
        pm2 = PresetManager(tmp_filepath)
        assert len(pm2.builds) == 1
        assert pm2.builds[0]["name"] == "Test Build"
        assert len(pm2.common_groups) == 1
        assert pm2.common_groups[0]["name"] == "Common A"

    def test_creates_directories(self, tmp_path):
        filepath = str(tmp_path / "sub" / "dir" / "presets.json")
        pm = PresetManager(filepath)
        pm.save()
        assert os.path.exists(filepath)


class TestBuildCRUD:
    def test_create_build_defaults(self, pm):
        build = pm.create_build("My Build")
        assert build["name"] == "My Build"
        assert "id" in build
        assert build["include_common"] is True
        assert build["common_group_ids"] == []
        assert build["min_matches"] == 2
        assert build["normal_whitelist"] == []
        assert build["deepnight_whitelist"] == []
        assert build["deepnight_neg_whitelist"] == []
        assert build["blacklist"] == []

    def test_get_build(self, pm):
        build = pm.create_build("B1")
        result = pm.get_build(build["id"])
        assert result is not None
        assert result["name"] == "B1"

    def test_get_build_not_found(self, pm):
        assert pm.get_build("nonexistent") is None

    def test_update_build(self, pm):
        build = pm.create_build("B1")
        pm.update_build(build["id"], name="B1 Updated", min_matches=3)
        updated = pm.get_build(build["id"])
        assert updated["name"] == "B1 Updated"
        assert updated["min_matches"] == 3

    def test_update_build_whitelist(self, pm):
        build = pm.create_build("B1")
        pm.update_build(build["id"], normal_whitelist=["aff1", "aff2"])
        updated = pm.get_build(build["id"])
        assert updated["normal_whitelist"] == ["aff1", "aff2"]

    def test_update_build_neg_and_blacklist(self, pm):
        build = pm.create_build("B1")
        pm.update_build(build["id"],
                        deepnight_neg_whitelist=["持续减少血量"],
                        blacklist=["降低物理减伤率"])
        updated = pm.get_build(build["id"])
        assert updated["deepnight_neg_whitelist"] == ["持续减少血量"]
        assert updated["blacklist"] == ["降低物理减伤率"]

    def test_delete_build(self, pm):
        build = pm.create_build("B1")
        pm.delete_build(build["id"])
        assert pm.get_build(build["id"]) is None
        assert len(pm.builds) == 0

    def test_auto_save_on_create(self, tmp_filepath):
        pm = PresetManager(tmp_filepath)
        pm.create_build("B1")
        pm2 = PresetManager(tmp_filepath)
        assert len(pm2.builds) == 1

    def test_auto_save_on_update(self, tmp_filepath):
        pm = PresetManager(tmp_filepath)
        build = pm.create_build("B1")
        pm.update_build(build["id"], name="Updated")
        pm2 = PresetManager(tmp_filepath)
        assert pm2.builds[0]["name"] == "Updated"

    def test_auto_save_on_delete(self, tmp_filepath):
        pm = PresetManager(tmp_filepath)
        build = pm.create_build("B1")
        pm.delete_build(build["id"])
        pm2 = PresetManager(tmp_filepath)
        assert len(pm2.builds) == 0


class TestCommonGroupCRUD:
    def test_create_common_group_defaults(self, pm):
        group = pm.create_common_group("CG1")
        assert group["name"] == "CG1"
        assert "id" in group
        assert group["normal_affixes"] == []
        assert group["deepnight_affixes"] == []
        assert group["deepnight_neg_affixes"] == []
        assert group["blacklist_affixes"] == []

    def test_get_common_group(self, pm):
        group = pm.create_common_group("CG1")
        result = pm.get_common_group(group["id"])
        assert result is not None
        assert result["name"] == "CG1"

    def test_get_common_group_not_found(self, pm):
        assert pm.get_common_group("nonexistent") is None

    def test_update_common_group(self, pm):
        group = pm.create_common_group("CG1")
        pm.update_common_group(group["id"], name="CG1 Updated", normal_affixes=["a1"])
        updated = pm.get_common_group(group["id"])
        assert updated["name"] == "CG1 Updated"
        assert updated["normal_affixes"] == ["a1"]

    def test_update_common_group_neg_and_blacklist(self, pm):
        group = pm.create_common_group("CG1")
        pm.update_common_group(group["id"],
                               deepnight_neg_affixes=["持续减少血量"],
                               blacklist_affixes=["降低物理减伤率"])
        updated = pm.get_common_group(group["id"])
        assert updated["deepnight_neg_affixes"] == ["持续减少血量"]
        assert updated["blacklist_affixes"] == ["降低物理减伤率"]

    def test_delete_common_group(self, pm):
        group = pm.create_common_group("CG1")
        pm.delete_common_group(group["id"])
        assert pm.get_common_group(group["id"]) is None

    def test_delete_common_group_cleans_build_refs(self, pm):
        group = pm.create_common_group("CG1")
        build = pm.create_build("B1")
        pm.update_build(build["id"], common_group_ids=[group["id"]])
        pm.delete_common_group(group["id"])
        updated_build = pm.get_build(build["id"])
        assert group["id"] not in updated_build["common_group_ids"]
