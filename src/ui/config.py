"""界面共享配置。"""

from __future__ import annotations

import sys

from PySide6.QtCore import QSize

WINDOW_TITLE = "Nightreign Relic Assistant"

WINDOW_CONFIG = {
	"title": WINDOW_TITLE,
	"width": 1200,
	"height": 750,
	"min_width": 1000,
	"min_height": 600,
}

NAVIGATION_CONFIG = {
	"icon_size": QSize(32, 32),
	"acrylic_enabled": True,
	"animation_enabled": False,
}


def detect_system_theme() -> str:
	"""Return the current Windows app theme when available."""
	if sys.platform != "win32":
		return "light"

	try:
		import winreg

		registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
		registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)
		value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
		winreg.CloseKey(registry_key)
		return "dark" if value == 0 else "light"
	except Exception:
		return "light"


THEME_CONFIG = {"theme": detect_system_theme()}
