"""长期记忆加载器（只读）。"""
from __future__ import annotations

from pathlib import Path


class MemoryLoader:
    def __init__(self, workspace: Path):
        self._memory_file = Path(workspace) / "memory" / "MEMORY.md"

    def load(self) -> str:
        """读取 MEMORY.md，拼装为 system prompt 段落。

        文件不存在或全空白时返回空串。
        """
        if not self._memory_file.exists():
            return ""
        content = self._memory_file.read_text(encoding="utf-8").strip()
        if not content:
            return ""
        return f"# Memory\n\n{content}"
