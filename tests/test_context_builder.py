"""ContextBuilder 单元测试。"""
from __future__ import annotations

from pathlib import Path

from agent.context import ContextBuilder
from memory.loader import MemoryLoader
from skills.loader import SkillsLoader


def _build(workspace: Path) -> ContextBuilder:
    return ContextBuilder(
        workspace=workspace,
        memory_loader=MemoryLoader(workspace),
        skills_loader=SkillsLoader(workspace),
    )


def test_system_prompt_starts_with_header(tmp_path: Path):
    prompt = _build(tmp_path).build_system_prompt()
    assert "Picobot" in prompt
    assert str(tmp_path) in prompt


def test_system_prompt_includes_existing_bootstrap_files(tmp_path: Path):
    (tmp_path / "SOUL.md").write_text("# Soul\n灵魂内容", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Agents\n规则", encoding="utf-8")
    prompt = _build(tmp_path).build_system_prompt()
    assert "灵魂内容" in prompt
    assert "规则" in prompt


def test_system_prompt_skips_missing_bootstrap_files(tmp_path: Path):
    prompt = _build(tmp_path).build_system_prompt()
    assert "## SOUL.md" not in prompt
    assert "## AGENTS.md" not in prompt


def test_system_prompt_injects_memory_section(tmp_path: Path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "MEMORY.md").write_text("- 偏好简洁", encoding="utf-8")
    prompt = _build(tmp_path).build_system_prompt()
    assert "# Memory" in prompt
    assert "偏好简洁" in prompt


def test_system_prompt_injects_skills_section(tmp_path: Path):
    skill_dir = tmp_path / "skills" / "search"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: search\ndescription: 搜索能力\n---\n# Search",
        encoding="utf-8",
    )
    prompt = _build(tmp_path).build_system_prompt()
    assert "<skills>" in prompt
    assert "搜索能力" in prompt


def test_build_messages_appends_user_with_timestamp(tmp_path: Path):
    builder = _build(tmp_path)
    messages = builder.build_messages([], "你好")
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert "你好" in messages[-1]["content"]
    assert "[Time:" in messages[-1]["content"]
