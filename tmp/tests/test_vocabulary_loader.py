from __future__ import annotations

from pathlib import Path

from infra.resources.vocabulary_loader import VocabularyLoader


def test_load_and_deduplicate_entries(tmp_path: Path):
    vocab_dir = tmp_path / "vocab"
    vocab_dir.mkdir()
    (vocab_dir / "a.txt").write_text("生命力+1\n1→生命力+2\n生命力+1\n", encoding="utf-8")
    loader = VocabularyLoader(primary_dir=vocab_dir, fallback_dir=vocab_dir)

    result = loader.load(["a.txt"])

    assert result == ["生命力+1", "生命力+2"]


def test_search_matches_case_insensitive(tmp_path: Path):
    vocab_dir = tmp_path / "vocab"
    vocab_dir.mkdir()
    loader = VocabularyLoader(primary_dir=vocab_dir, fallback_dir=vocab_dir)

    result = loader.search("火", ["提升火属性攻击力", "提升雷属性攻击力"])

    assert result == ["提升火属性攻击力"]
