"""Skills loader 单元测试。"""
from __future__ import annotations

from pathlib import Path

from skills.loader import SkillsLoader


def _make_skill(root: Path, name: str, description: str | None = None) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    if description:
        body = f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n"
    else:
        body = f"# {name}\n"
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def test_lists_skills_from_workspace(tmp_path: Path):
    workspace = tmp_path / "ws"
    _make_skill(workspace / "skills", "search", "搜索网络")
    loader = SkillsLoader(workspace)
    names = [skill["name"] for skill in loader.list_skills()]
    assert names == ["search"]


def test_workspace_skill_overrides_builtin(tmp_path: Path):
    workspace = tmp_path / "ws"
    builtin = tmp_path / "builtin"
    _make_skill(workspace / "skills", "search", "ws 版")
    _make_skill(builtin, "search", "builtin 版")
    loader = SkillsLoader(workspace, builtin_dir=builtin)
    skills = loader.list_skills()
    assert len(skills) == 1
    assert skills[0]["description"] == "ws 版"


def test_description_falls_back_to_directory_name(tmp_path: Path):
    workspace = tmp_path / "ws"
    _make_skill(workspace / "skills", "demo")
    loader = SkillsLoader(workspace)
    skills = loader.list_skills()
    assert skills[0]["description"] == "demo"


def test_build_summary_returns_empty_when_no_skills(tmp_path: Path):
    loader = SkillsLoader(tmp_path / "ws")
    assert loader.build_skills_summary() == ""


def test_build_summary_wraps_skills_in_xml(tmp_path: Path):
    workspace = tmp_path / "ws"
    _make_skill(workspace / "skills", "search", "搜索网络")
    summary = SkillsLoader(workspace).build_skills_summary()
    assert summary.startswith("<skills>")
    assert summary.endswith("</skills>")
    assert "search" in summary
    assert "搜索网络" in summary
