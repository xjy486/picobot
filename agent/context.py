"""System prompt 与消息列表构造。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from memory.loader import MemoryLoader
from skills.loader import SkillsLoader


class ContextBuilder:
    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

    def __init__(
        self,
        workspace: Path,
        memory_loader: MemoryLoader,
        skills_loader: SkillsLoader | None = None,
    ):
        self.workspace = Path(workspace)
        self._memory = memory_loader
        self._skills = skills_loader

    def build_system_prompt(self) -> str:
        parts = [
            f"# Picobot\n\n你是一个有帮助的 AI 助手。\n\n"
            f"工作区: {self.workspace}\n"
            f"长期记忆: {self.workspace}/memory/MEMORY.md"
        ]
        for filename in self.BOOTSTRAP_FILES:
            path = self.workspace / filename
            if path.exists():
                parts.append(f"## {filename}\n\n{path.read_text(encoding='utf-8')}")
        memory = self._memory.load()
        if memory:
            parts.append(memory)
        if self._skills is not None:
            skills_section = self._skills.build_skills_summary()
            if skills_section:
                parts.append(skills_section)
        return "\n\n---\n\n".join(parts)

    def build_messages(self, history: list[dict], user_message: str) -> list[dict]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": f"[Time: {now}]\n\n{user_message}"},
        ]
