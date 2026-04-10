"""词条文件加载与搜索工具。"""

from __future__ import annotations

from pathlib import Path

from infra.system.paths import get_data_dir


class VocabularyLoader:
    def __init__(self, primary_dir: Path | None = None, fallback_dir: Path | None = None):
        self.primary_dir = primary_dir or get_data_dir()
        self.fallback_dir = fallback_dir
        self._cache: dict[tuple[str, ...], list[str]] = {}

    def load(self, filenames: list[str]) -> list[str]:
        key = tuple(filenames)
        if key in self._cache:
            return list(self._cache[key])

        results: list[str] = []
        seen: set[str] = set()

        search_dirs = [self.primary_dir]
        if self.fallback_dir is not None:
            search_dirs.append(self.fallback_dir)

        for filename in filenames:
            for base_dir in search_dirs:
                path = base_dir / filename
                if not path.exists():
                    continue
                self._read_file(path, seen, results)
                break

        self._cache[key] = list(results)
        return results

    def search(self, query: str, vocabulary: list[str]) -> list[str]:
        if not query:
            return list(vocabulary)
        lowered = query.lower()
        return [entry for entry in vocabulary if lowered in entry.lower()]

    @staticmethod
    def _read_file(path: Path, seen: set[str], results: list[str]) -> None:
        with path.open("r", encoding="utf-8-sig") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                if "→" in line:
                    line = line.split("→", 1)[1].strip()
                if line and line not in seen:
                    seen.add(line)
                    results.append(line)
