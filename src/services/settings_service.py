"""设置读写业务服务。"""

from __future__ import annotations

from dataclasses import asdict, replace

from core.models.runtime import AppSettings
from infra.persistence.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository):
        self.repository = repository
        self._settings = self.repository.load_settings()

    def get_settings(self) -> AppSettings:
        return replace(self._settings)

    def update_settings(self, **changes) -> AppSettings:
        data = asdict(self._settings)
        data.update(changes)
        self._settings = AppSettings(**data)
        self.repository.save_settings(self._settings)
        return self.get_settings()
