"""设置仓储读写辅助。"""

from __future__ import annotations

from dataclasses import asdict

from core.models.runtime import AppSettings, build_default_settings
from infra.persistence.json_store import JsonFileRepository
from infra.system.paths import get_settings_path


class SettingsRepository(JsonFileRepository):
    def __init__(self):
        super().__init__(get_settings_path(), lambda: asdict(build_default_settings()))

    def load_settings(self) -> AppSettings:
        payload = self.load()
        defaults = asdict(build_default_settings())
        defaults.update(payload)
        return AppSettings(**defaults)

    def save_settings(self, settings: AppSettings) -> None:
        self.save(asdict(settings))
