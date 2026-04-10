"""商店与仓库历史记录仓储。"""

from __future__ import annotations

from infra.persistence.json_store import JsonFileRepository
from infra.system.paths import (
    get_repo_favorited_history_path,
    get_repo_sold_history_path,
    get_shop_history_path,
)


class RelicHistoryRepository(JsonFileRepository):
    def __init__(self, path_factory):
        super().__init__(path_factory(), lambda: {"records": []})

    def load_records(self) -> list[dict]:
        payload = self.load()
        return list(payload.get("records", []))

    def save_records(self, records: list[dict]) -> None:
        self.save({"records": list(records)})

    def append_record(self, record: dict) -> None:
        records = self.load_records()
        records.append(record)
        self.save_records(records)

    def clear(self) -> None:
        self.save({"records": []})


def build_history_repositories() -> dict[str, RelicHistoryRepository]:
    return {
        "shop_qualified": RelicHistoryRepository(get_shop_history_path),
        "repo_sold": RelicHistoryRepository(get_repo_sold_history_path),
        "repo_favorited": RelicHistoryRepository(get_repo_favorited_history_path),
    }
