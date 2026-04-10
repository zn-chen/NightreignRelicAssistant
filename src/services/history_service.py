"""历史记录持久化服务。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from infra.persistence.history_repository import RelicHistoryRepository


class HistoryService:
    def __init__(self, repositories: dict[str, RelicHistoryRepository]):
        self.repositories = repositories

    def list_records(self, bucket: str) -> list[dict]:
        return self._repo(bucket).load_records()

    def add_record(self, bucket: str, *, source: str, index: int, affixes: list[dict], extra: dict | None = None) -> dict:
        # 历史记录统一在服务层补齐主键和时间戳，页面与业务流程只传业务字段。
        record = {
            "record_id": str(uuid4()),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "source": source,
            "index": index,
            "affixes": affixes,
            "extra": extra or {},
        }
        self._repo(bucket).append_record(record)
        return record

    def clear(self, bucket: str) -> None:
        self._repo(bucket).clear()

    def _repo(self, bucket: str) -> RelicHistoryRepository:
        if bucket not in self.repositories:
            raise KeyError(f"Unknown history bucket: {bucket}")
        return self.repositories[bucket]
