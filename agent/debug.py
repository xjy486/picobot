"""调试日志模块。

当 PICOBOT_DEBUG=1 时，将每一轮对话的完整上下文写入 JSONL 日志文件，
文件名带启动时间戳，便于排查 LLM 交互问题。
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path


class DebugLogger:
    """异步安全的调试上下文日志器。

    日志文件位于 ``{workspace}/logs/debug_YYYYMMDD_HHMMSS.jsonl``，
    每一行是一条 JSON 记录，包含时间戳、会话标识、阶段和完整 messages 列表。
    """

    def __init__(self, workspace: Path) -> None:
        self._enabled = False
        self._log_path: Path | None = None
        self._lock = asyncio.Lock()

    def enable(self, workspace: Path) -> None:
        """基于 workspace 创建日志目录和带时间戳的日志文件。"""
        logs_dir = workspace / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_path = logs_dir / f"debug_{timestamp}.jsonl"
        self._enabled = True

    async def log_context(
        self,
        session_key: str,
        phase: str,
        messages: list[dict],
    ) -> None:
        """追加一条上下文记录到日志文件（若已启用）。"""
        if not self._enabled or self._log_path is None:
            return
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_key": session_key,
            "phase": phase,
            "message_count": len(messages),
            "messages": messages,
        }
        line = json.dumps(entry, ensure_ascii=False)
        async with self._lock:
            with open(self._log_path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
