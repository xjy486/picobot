"""Tools 模块单元测试。"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.base import ToolRegistry
from tools.exec import ExecTool
from tools.files import ReadFileTool, WriteFileTool


def test_tool_to_schema_shape():
    tool = ExecTool()
    schema = tool.to_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "exec"
    assert "command" in schema["function"]["parameters"]["properties"]


@pytest.mark.asyncio
async def test_exec_tool_blocks_dangerous_command():
    tool = ExecTool()
    result = await tool.execute(command="rm -rf /")
    assert result.startswith("Error: Blocked")


@pytest.mark.asyncio
async def test_read_file_tool_returns_error_for_missing_path(tmp_path: Path):
    tool = ReadFileTool()
    missing = tmp_path / "does_not_exist.txt"
    result = await tool.execute(path=str(missing))
    assert "Not found" in result


@pytest.mark.asyncio
async def test_write_file_tool_creates_parent_dirs(tmp_path: Path):
    tool = WriteFileTool()
    target = tmp_path / "nested" / "deep" / "out.txt"
    result = await tool.execute(path=str(target), content="hello")
    assert target.read_text(encoding="utf-8") == "hello"
    assert "Wrote" in result


def test_tool_registry_lists_registered_tools():
    registry = ToolRegistry()
    registry.register(ExecTool())
    names = {definition["function"]["name"] for definition in registry.get_definitions()}
    assert "exec" in names


@pytest.mark.asyncio
async def test_tool_registry_unknown_tool_returns_error():
    registry = ToolRegistry()
    result = await registry.execute("nope", {})
    assert "Unknown tool" in result
