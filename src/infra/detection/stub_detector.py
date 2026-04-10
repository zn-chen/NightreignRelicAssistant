"""安全占位的遗物状态检测器。"""

from __future__ import annotations

from core.interfaces import IRelicStateDetector


class StubRelicStateDetector(IRelicStateDetector):
    def is_ready(self) -> bool:
        return False

    def detect_relic_state(self, screenshot) -> str:
        _ = screenshot
        return "unknown"
