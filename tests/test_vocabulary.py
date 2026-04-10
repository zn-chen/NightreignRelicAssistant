"""VocabularyLoader tests."""

import os
import tempfile

import pytest

from nra.models.vocabulary import VocabularyLoader


@pytest.fixture
def tmp_data(tmp_path):
    """Create temporary data files for testing."""
    # file_a.txt
    (tmp_path / "file_a.txt").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    # file_b.txt
    (tmp_path / "file_b.txt").write_text("delta\nepsilon\n", encoding="utf-8")
    # file with arrow format
    (tmp_path / "arrows.txt").write_text(
        "raw1\nfoo → bar\nbaz → qux\nraw2\n", encoding="utf-8"
    )
    # file with BOM
    (tmp_path / "bom.txt").write_bytes(
        b"\xef\xbb\xbfbom_line1\nbom_line2\n"
    )
    # file with duplicates relative to file_a
    (tmp_path / "dup.txt").write_text("alpha\nnew_item\n", encoding="utf-8")
    return tmp_path


class TestLoad:
    def test_load_single_file(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["file_a.txt"])
        assert result == ["alpha", "beta", "gamma"]

    def test_load_multiple_files(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["file_a.txt", "file_b.txt"])
        assert result == ["alpha", "beta", "gamma", "delta", "epsilon"]

    def test_load_nonexistent_file_returns_empty(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["no_such_file.txt"])
        assert result == []

    def test_load_deduplicates_same_file_twice(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["file_a.txt", "file_a.txt"])
        assert result == ["alpha", "beta", "gamma"]

    def test_load_deduplicates_across_files(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["file_a.txt", "dup.txt"])
        assert result == ["alpha", "beta", "gamma", "new_item"]

    def test_load_handles_arrow_format(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["arrows.txt"])
        assert result == ["raw1", "bar", "qux", "raw2"]

    def test_load_handles_bom(self, tmp_data):
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["bom.txt"])
        assert result == ["bom_line1", "bom_line2"]

    def test_load_skips_blank_lines(self, tmp_data):
        (tmp_data / "blanks.txt").write_text("a\n\nb\n  \nc\n", encoding="utf-8")
        loader = VocabularyLoader(str(tmp_data))
        result = loader.load(["blanks.txt"])
        assert result == ["a", "b", "c"]


class TestSearch:
    def test_search_exact_match(self):
        loader = VocabularyLoader("")
        vocab = ["alpha", "beta", "gamma"]
        assert loader.search("alpha", vocab) == ["alpha"]

    def test_search_partial_match(self):
        loader = VocabularyLoader("")
        vocab = ["alpha", "beta", "gamma"]
        assert loader.search("al", vocab) == ["alpha"]

    def test_search_empty_query_returns_all(self):
        loader = VocabularyLoader("")
        vocab = ["alpha", "beta", "gamma"]
        assert loader.search("", vocab) == ["alpha", "beta", "gamma"]

    def test_search_no_match_returns_empty(self):
        loader = VocabularyLoader("")
        vocab = ["alpha", "beta", "gamma"]
        assert loader.search("zzz", vocab) == []

    def test_search_multiple_matches(self):
        loader = VocabularyLoader("")
        vocab = ["生命力+1", "生命力+2", "集中力+1"]
        assert loader.search("生命力", vocab) == ["生命力+1", "生命力+2"]
