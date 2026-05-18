"""DebugLogger 单元测试。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.debug import DebugLogger


@pytest.mark.asyncio
async def test_enable_creates_timestamped_file(tmp_path: Path):
    """enable() 应在 workspace/logs/ 下创建带时间戳的 jsonl 文件。"""
    logger = DebugLogger(tmp_path)
    logger.enable(tmp_path)
    assert logger._enabled
    assert logger._log_path is not None
    assert logger._log_path.parent.name == "logs"
    assert logger._log_path.suffix == ".jsonl"
    assert logger._log_path.stem.startswith("debug_")


@pytest.mark.asyncio
async def test_log_context_writes_valid_jsonl(tmp_path: Path):
    """log_context() 应写入一行可解析的 JSON，包含预期字段。"""
    logger = DebugLogger(tmp_path)
    logger.enable(tmp_path)

    messages = [
        {"role": "system", "content": "you are a bot"},
        {"role": "user", "content": "hi"},
    ]
    await logger.log_context("cli:direct", "start", messages)

    lines = logger._log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["session_key"] == "cli:direct"
    assert record["phase"] == "start"
    assert record["message_count"] == 2
    assert record["messages"] == messages
    assert "timestamp" in record


@pytest.mark.asyncio
async def test_log_context_appends_multiple_lines(tmp_path: Path):
    """多次调用 log_context() 应在同一文件追加多行。"""
    logger = DebugLogger(tmp_path)
    logger.enable(tmp_path)

    await logger.log_context("cli:direct", "start", [{"role": "user", "content": "a"}])
    await logger.log_context("cli:direct", "react_0", [{"role": "user", "content": "a"}])

    lines = logger._log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["phase"] == "start"
    assert json.loads(lines[1])["phase"] == "react_0"


@pytest.mark.asyncio
async def test_log_context_noop_when_disabled(tmp_path: Path):
    """未启用时 log_context() 不应创建文件或写入任何内容。"""
    logger = DebugLogger(tmp_path)
    # 不调用 enable()
    await logger.log_context("cli:direct", "start", [{"role": "user", "content": "hi"}])
    assert not logger._enabled
    assert logger._log_path is None
    # logs 目录不应被创建
    assert not (tmp_path / "logs").exists()
