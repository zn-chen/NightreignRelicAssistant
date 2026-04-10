"""词缀词库加载与检索。"""

from __future__ import annotations

import os


class VocabularyLoader:
    """加载并检索词缀词库。"""

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir

    def load(self, files: list[str]) -> list[str]:
        """从指定文件加载词缀，去重并保持顺序。

        跳过不存在的文件，处理 ``→`` 格式（取右侧），
        使用 utf-8-sig 编码以兼容 BOM。
        """
        seen: set[str] = set()
        result: list[str] = []
        for filename in files:
            path = os.path.join(self.data_dir, filename)
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8-sig") as f:
                for line in f:
                    entry = line.strip()
                    if not entry:
                        continue
                    if "→" in entry:
                        entry = entry.split("→", 1)[1].strip()
                    if entry not in seen:
                        seen.add(entry)
                        result.append(entry)
        return result

    def search(self, query: str, vocabulary: list[str]) -> list[str]:
        """检索词缀。空查询返回全部，否则按子串匹配过滤。"""
        if not query:
            return list(vocabulary)
        return [item for item in vocabulary if query in item]
