"""文件读写工具。"""
from __future__ import annotations

from pathlib import Path

from tools.base import Tool


class ReadFileTool(Tool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read file contents."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
            },
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs) -> str:
        target = Path(path).expanduser()
        if not target.exists():
            return f"Error: Not found: {path}"
        try:
            return target.read_text(encoding="utf-8")[:50000]
        except Exception as exc:
            return f"Error: {exc}"


class WriteFileTool(Tool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content"},
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, **kwargs) -> str:
        try:
            target = Path(path).expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} bytes to {target}"
        except Exception as exc:
            return f"Error: {exc}"
