"""预设仓储读写辅助。"""

from __future__ import annotations

from core.models.preset import PresetRecord, PresetStore, build_default_preset_store
from infra.persistence.json_store import JsonFileRepository
from infra.system.paths import get_presets_path


class PresetRepository(JsonFileRepository):
    def __init__(self):
        super().__init__(get_presets_path(), self._build_default_payload)

    @staticmethod
    def _build_default_payload() -> dict:
        # 默认文件仍然以纯 JSON 结构保存，避免把 dataclass 表达直接泄露到磁盘格式里。
        store = build_default_preset_store()
        return {
            "version": store.version,
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
                for preset in store.presets
            ],
        }

    def load_store(self) -> PresetStore:
        # 读取磁盘 JSON 后在仓储层还原成业务模型，服务层不再关心底层字段细节。
        payload = self.load()
        presets = [
            PresetRecord(
                preset_id=item["preset_id"],
                name=item["name"],
                enabled=item.get("enabled", True),
                order=item.get("order", 0),
                normal_relic_affixes=list(item.get("normal_relic_affixes", [])),
                deepnight_relic_affixes=list(item.get("deepnight_relic_affixes", [])),
                blacklist_affixes=list(item.get("blacklist_affixes", [])),
            )
            for item in payload.get("presets", [])
        ]
        return PresetStore(version=payload.get("version", 3), presets=presets)

    def save_store(self, store: PresetStore) -> None:
        # 保存前重新展开 dataclass，确保输出结构稳定且便于手工查看与导入导出。
        self.save(
            {
                "version": store.version,
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
                    for preset in store.presets
                ],
            }
        )
