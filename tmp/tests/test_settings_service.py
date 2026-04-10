from __future__ import annotations

from pathlib import Path

from infra.persistence.settings_repository import SettingsRepository
from services.settings_service import SettingsService


class TemporarySettingsRepository(SettingsRepository):
    def __init__(self, path: Path):
        self.path = path
        self.default_factory = lambda: {
            "steam_path": "",
            "theme": "light",
            "show_welcome": True,
            "developer_mode": False,
            "allow_operate_favorited": False,
            "require_double_valid": True,
            "shop_require_double_valid": True,
            "ocr_debug": False,
            "template_threshold": 0.7,
            "brightness_threshold": 45,
            "sl_mode_enabled": False,
            "backup_dir": "data/save_backups",
            "notification_enabled": False,
            "notification_webhook": "",
        }


def test_update_settings_persists_to_disk(tmp_path: Path):
    repository = TemporarySettingsRepository(tmp_path / "settings.json")
    service = SettingsService(repository)

    updated = service.update_settings(steam_path="C:/Steam", developer_mode=True)

    assert updated.steam_path == "C:/Steam"
    assert updated.developer_mode is True
    assert repository.load()["steam_path"] == "C:/Steam"
