"""预设持久化相关模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PresetRecord:
    preset_id: str
    name: str
    enabled: bool = True
    order: int = 0
    normal_relic_affixes: list[str] = field(default_factory=list)
    deepnight_relic_affixes: list[str] = field(default_factory=list)
    blacklist_affixes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PresetStore:
    version: int = 3
    presets: list[PresetRecord] = field(default_factory=list)


def build_default_preset_store() -> PresetStore:
    return PresetStore(
        version=3,
        presets=[
            PresetRecord(
                preset_id="default_preset",
                name="默认预设",
                enabled=True,
                order=0,
            ),
        ],
    )

