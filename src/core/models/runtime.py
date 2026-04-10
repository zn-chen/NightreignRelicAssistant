"""运行时配置与统计模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AppSettings:
    steam_path: str = ""
    theme: str = "light"
    show_welcome: bool = True
    developer_mode: bool = False
    allow_operate_favorited: bool = False
    require_double_valid: bool = True
    shop_require_double_valid: bool = True
    ocr_debug: bool = False
    template_threshold: float = 0.7
    brightness_threshold: int = 45
    sl_mode_enabled: bool = False
    backup_dir: str = "data/save_backups"
    notification_enabled: bool = False
    notification_webhook: str = ""


def build_default_settings() -> AppSettings:
    return AppSettings()


@dataclass(slots=True)
class TaskStats:
    counters: dict[str, int] = field(default_factory=dict)

    def set_default(self, keys: list[str]) -> None:
        for key in keys:
            self.counters.setdefault(key, 0)
