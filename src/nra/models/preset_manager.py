"""PresetManager — CRUD for builds, common groups, and blacklist groups."""

from __future__ import annotations

import json
import os
import uuid


class PresetManager:
    """Manages preset data: builds, common groups, and blacklist groups."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.builds: list[dict] = []
        self.common_groups: list[dict] = []
        self.blacklist_groups: list[dict] = []
        self._load()

    # ── Persistence ──────────────────────────────────────────────

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        data = {
            "builds": self.builds,
            "common_groups": self.common_groups,
            "blacklist_groups": self.blacklist_groups,
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.builds = data.get("builds", [])
        self.common_groups = data.get("common_groups", [])
        self.blacklist_groups = data.get("blacklist_groups", [])

    # ── Build CRUD ───────────────────────────────────────────────

    def create_build(self, name: str) -> dict:
        build = {
            "id": str(uuid.uuid4()),
            "name": name,
            "include_common": True,
            "common_group_ids": [],
            "blacklist_group_ids": [],
            "min_matches": 2,
            "normal_whitelist": [],
            "deepnight_whitelist": [],
        }
        self.builds.append(build)
        self.save()
        return build

    def get_build(self, build_id: str) -> dict | None:
        for b in self.builds:
            if b["id"] == build_id:
                return b
        return None

    def update_build(self, build_id: str, **kwargs) -> None:
        build = self.get_build(build_id)
        if build is None:
            return
        for key, value in kwargs.items():
            if key in build:
                build[key] = value
        self.save()

    def delete_build(self, build_id: str) -> None:
        self.builds = [b for b in self.builds if b["id"] != build_id]
        self.save()

    # ── Common Group CRUD ────────────────────────────────────────

    def create_common_group(self, name: str) -> dict:
        group = {
            "id": str(uuid.uuid4()),
            "name": name,
            "normal_affixes": [],
            "deepnight_affixes": [],
        }
        self.common_groups.append(group)
        self.save()
        return group

    def get_common_group(self, group_id: str) -> dict | None:
        for g in self.common_groups:
            if g["id"] == group_id:
                return g
        return None

    def update_common_group(self, group_id: str, **kwargs) -> None:
        group = self.get_common_group(group_id)
        if group is None:
            return
        for key, value in kwargs.items():
            if key in group:
                group[key] = value
        self.save()

    def delete_common_group(self, group_id: str) -> None:
        self.common_groups = [g for g in self.common_groups if g["id"] != group_id]
        for build in self.builds:
            if group_id in build["common_group_ids"]:
                build["common_group_ids"].remove(group_id)
        self.save()

    # ── Blacklist Group CRUD ─────────────────────────────────────

    def create_blacklist_group(self, name: str) -> dict:
        group = {
            "id": str(uuid.uuid4()),
            "name": name,
            "affixes": [],
        }
        self.blacklist_groups.append(group)
        self.save()
        return group

    def get_blacklist_group(self, group_id: str) -> dict | None:
        for g in self.blacklist_groups:
            if g["id"] == group_id:
                return g
        return None

    def update_blacklist_group(self, group_id: str, **kwargs) -> None:
        group = self.get_blacklist_group(group_id)
        if group is None:
            return
        for key, value in kwargs.items():
            if key in group:
                group[key] = value
        self.save()

    def delete_blacklist_group(self, group_id: str) -> None:
        self.blacklist_groups = [g for g in self.blacklist_groups if g["id"] != group_id]
        for build in self.builds:
            if group_id in build["blacklist_group_ids"]:
                build["blacklist_group_ids"].remove(group_id)
        self.save()
