"""预设业务与词库访问服务。"""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.models.preset import PresetRecord, PresetStore
from infra.persistence.preset_repository import PresetRepository
from infra.resources.vocabulary_loader import VocabularyLoader


MAX_PRESET_COUNT = 20


class PresetService:
    def __init__(self, repository: PresetRepository, vocabulary_loader: VocabularyLoader):
        self.repository = repository
        self.vocabulary_loader = vocabulary_loader
        self.store = self.repository.load_store()

    def reload(self) -> None:
        self.store = self.repository.load_store()

    def load_vocabulary(self, preset_field: str) -> list[str]:
        # 词库按预设字段分组加载，让编辑弹窗只拿到当前场景真正关心的候选项。
        if preset_field == "normal_relic":
            files = ["normal.txt", "normal_special.txt"]
        elif preset_field == "deepnight_relic":
            files = ["deepnight_pos.txt", "deepnight_neg.txt"]
        elif preset_field == "blacklist":
            files = ["normal.txt", "normal_special.txt", "deepnight_pos.txt", "deepnight_neg.txt"]
        else:
            return []

        vocabulary = self.vocabulary_loader.load(files)
        return list(dict.fromkeys(vocabulary))

    def list_presets(self, *, enabled_only: bool = False) -> list[PresetRecord]:
        # 返回前统一按排序字段整理，并克隆对象避免 UI 直接改到仓储内存。
        presets = list(self.store.presets)
        presets.sort(key=lambda item: item.order)
        if enabled_only:
            presets = [preset for preset in presets if preset.enabled]
        return [replace(preset) for preset in presets]

    def get_preset(self, preset_id: str) -> PresetRecord | None:
        return self._clone_optional(self._find_one(preset_id=preset_id))

    def create_preset(
        self,
        name: str,
        normal_relic_affixes: list[str],
        deepnight_relic_affixes: list[str],
        blacklist_affixes: list[str],
    ) -> PresetRecord:
        presets = self.list_presets()
        if len(presets) >= MAX_PRESET_COUNT:
            raise ValueError(f"预设数量已达上限（{MAX_PRESET_COUNT}个）")

        next_order = max((preset.order for preset in presets), default=-1) + 1
        preset = PresetRecord(
            preset_id=str(uuid4()),
            name=name,
            enabled=True,
            order=next_order,
            normal_relic_affixes=list(normal_relic_affixes),
            deepnight_relic_affixes=list(deepnight_relic_affixes),
            blacklist_affixes=list(blacklist_affixes),
        )
        self.store.presets.append(preset)
        self._save()
        return replace(preset)

    def update_preset(
        self,
        preset_id: str,
        *,
        name: str | None = None,
        normal_relic_affixes: list[str] | None = None,
        deepnight_relic_affixes: list[str] | None = None,
        blacklist_affixes: list[str] | None = None,
    ) -> PresetRecord:
        preset = self._find_by_id_required(preset_id)
        if name is not None:
            preset.name = name
        if normal_relic_affixes is not None:
            preset.normal_relic_affixes = list(normal_relic_affixes)
        if deepnight_relic_affixes is not None:
            preset.deepnight_relic_affixes = list(deepnight_relic_affixes)
        if blacklist_affixes is not None:
            preset.blacklist_affixes = list(blacklist_affixes)
        self._save()
        return replace(preset)

    def delete_preset(self, preset_id: str) -> None:
        self._find_by_id_required(preset_id)
        self.store.presets = [item for item in self.store.presets if item.preset_id != preset_id]
        self._reindex()
        self._save()

    def toggle_preset_enabled(self, preset_id: str) -> PresetRecord:
        preset = self._find_by_id_required(preset_id)
        preset.enabled = not preset.enabled
        self._save()
        return replace(preset)

    def reorder_presets(self, source_id: str, target_id: str) -> list[PresetRecord]:
        presets = self.list_presets()
        ids = [item.preset_id for item in presets]

        if source_id not in ids or target_id not in ids or source_id == target_id:
            return presets

        # 拖拽排序只重算 order，不改预设内容本身。
        source_index = ids.index(source_id)
        target_index = ids.index(target_id)
        ids.pop(source_index)
        ids.insert(target_index, source_id)

        order_map = {value: index for index, value in enumerate(ids)}
        for item in self.store.presets:
            if item.preset_id in order_map:
                item.order = order_map[item.preset_id]

        self._save()
        return self.list_presets()

    def export_payload(self) -> dict:
        return {
            "version": self.store.version,
            "presets": [
                {
                    "preset_id": preset.preset_id,
                    "name": preset.name,
                    "enabled": preset.enabled,
                    "order": preset.order,
                    "normal_relic_affixes": list(preset.normal_relic_affixes),
                    "deepnight_relic_affixes": list(preset.deepnight_relic_affixes),
                    "blacklist_affixes": list(preset.blacklist_affixes),
                }
                for preset in self.store.presets
            ],
        }

    def import_payload(self, payload: dict) -> None:
        # 导入时全部重建为内部模型，再统一重排 order，避免脏数据直接进入运行态。
        presets = []
        for raw in payload.get("presets", []):
            presets.append(
                PresetRecord(
                    preset_id=raw["preset_id"],
                    name=raw["name"],
                    enabled=raw.get("enabled", True),
                    order=raw.get("order", 0),
                    normal_relic_affixes=list(raw.get("normal_relic_affixes", [])),
                    deepnight_relic_affixes=list(raw.get("deepnight_relic_affixes", [])),
                    blacklist_affixes=list(raw.get("blacklist_affixes", [])),
                )
            )
        self.store = PresetStore(version=payload.get("version", 3), presets=presets)
        self._reindex()
        self._save()

    def _find_one(self, **filters) -> PresetRecord | None:
        for preset in self.store.presets:
            if all(getattr(preset, key) == value for key, value in filters.items()):
                return preset
        return None

    def _find_by_id_required(self, preset_id: str) -> PresetRecord:
        for preset in self.store.presets:
            if preset.preset_id == preset_id:
                return preset
        raise ValueError(f"Preset not found: {preset_id}")

    def _reindex(self) -> None:
        ordered = sorted(self.store.presets, key=lambda item: item.order)
        for index, item in enumerate(ordered):
            item.order = index

    def _save(self) -> None:
        self.repository.save_store(self.store)

    @staticmethod
    def _clone_optional(preset: PresetRecord | None) -> PresetRecord | None:
        return replace(preset) if preset is not None else None
