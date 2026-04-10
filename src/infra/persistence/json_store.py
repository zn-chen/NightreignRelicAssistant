"""通用 JSON 文件持久化封装。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.interfaces import IJsonRepository


class JsonFileRepository(IJsonRepository):
    def __init__(self, path: Path, default_factory):
        self.path = path
        self.default_factory = default_factory

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            payload = self.default_factory()
            self.save(payload)
            return payload

        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
