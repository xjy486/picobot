"""Memory loader 单元测试。"""
from __future__ import annotations

from pathlib import Path

from memory.loader import MemoryLoader


def test_load_returns_empty_string_when_file_missing(tmp_path: Path):
    loader = MemoryLoader(tmp_path)
    assert loader.load() == ""


def test_load_returns_empty_string_when_file_blank(tmp_path: Path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "MEMORY.md").write_text("   \n  \n", encoding="utf-8")
    loader = MemoryLoader(tmp_path)
    assert loader.load() == ""


def test_load_returns_section_when_file_has_content(tmp_path: Path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "MEMORY.md").write_text("- 用户偏好简洁回复", encoding="utf-8")
    loader = MemoryLoader(tmp_path)
    result = loader.load()
    assert "Memory" in result
    assert "用户偏好简洁回复" in result
