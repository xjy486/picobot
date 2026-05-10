# Picobot 项目结构拆分实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 把现有 `agent-gateway.py` 等单文件快照按照规格拆分为模块化包结构，落地为可工作、可测试的极简 Picobot。

**架构：** 扁平包结构（`app.py` + `config.py` + 7 个一级 Python 包：`agent`/`channels`/`memory`/`providers`/`session`/`skills`/`tools`）。`AgentLoop` 通过 `Provider` 接口与 LLM 解耦；`MessageBus` 解耦 channels 与 agent；`workspace/` 仅作默认模板，运行时数据落到 `~/.picobot/workspace`。

**技术栈：** Python ≥ 3.10，`openai>=1.0`（同步 SDK，包到 `asyncio.to_thread` 中），可选 `python-dotenv`，测试用 `pytest` + `pytest-asyncio`。setuptools 后端 + PEP 621 `pyproject.toml`。

**与规格的两处微调：**

1. 规格的 commit 13 步序列里有独立的 `test: 补齐核心单元测试`。本计划遵循 TDD，测试与对应模块实现一起 commit，因此该步骤被吸收到各 feat commit 中，序列缩为 12 步。
2. 规格的 commit 1（`chore: 初始化项目骨架`）在本计划中**额外把现有 4 个旧 `.py` 文件（脱敏后）一并 git add**。这样 commit 11（`chore: 删除旧快照`）才能真正 `git rm`、留下有意义的版本轨迹，否则文件从未被 tracked，删除对 git 不可见。

**最终 commit 序列（含已 commit 的 2 个 docs commit）：**

```
[已存在]  09e9718  docs: 添加 picobot 重构设计规格
[已存在]  a838c9c  docs: 规格自检修订（补全 ToolCall 定义、统一扁平结构启动命令）
[本计划]  1.  chore: 初始化项目骨架，纳入现有快照代码
[本计划]  2.  feat(config): 引入 Config 与环境变量加载
[本计划]  3.  feat(providers): 抽象 Provider 接口与 OpenAI 实现
[本计划]  4.  feat(tools): 拆分工具系统至 tools/ 目录（含测试）
[本计划]  5.  feat(session): 迁移会话管理至 session/ 目录（含测试）
[本计划]  6.  feat(memory): 提取 MemoryLoader 模块（含测试）
[本计划]  7.  feat(skills): 接入 SkillsLoader 与 skills/ 目录（含测试）
[本计划]  8.  feat(agent): 落地 ContextBuilder 与 AgentLoop（含 ContextBuilder 测试）
[本计划]  9.  feat(channels): 拆分消息总线与 CLI 渠道（含 MessageBus 测试）
[本计划]  10. feat(app): 装配入口 app.py
[本计划]  11. chore: 删除旧快照（agent-tool/agent-memory/agent-gateway/skills-loader）
[本计划]  12. docs: 完善 README
```

---

## 文件结构

| 路径 | 创建 / 修改 | 职责 |
|---|---|---|
| `pyproject.toml` | 创建 | PEP 621 项目元数据、依赖、pytest 配置 |
| `.env.example` | 创建 | 环境变量模板（不放真实 key） |
| `README.md` | 创建（任务 1）→ 重写（任务 12） | 项目说明 + 运行指南 |
| `app.py` | 创建（任务 10） | 装配入口，启动 gateway |
| `config.py` | 创建（任务 2） | `Config.from_env()` |
| `providers/__init__.py` | 创建 | 包标记 |
| `providers/base.py` | 创建（任务 3） | `Provider` / `ProviderResponse` / `ToolCall` |
| `providers/openai.py` | 创建（任务 3） | `OpenAIProvider` |
| `tools/__init__.py` | 创建 | 包标记 |
| `tools/base.py` | 创建（任务 4） | `Tool` / `ToolRegistry` |
| `tools/exec.py` | 创建（任务 4） | `ExecTool` |
| `tools/files.py` | 创建（任务 4） | `ReadFileTool` / `WriteFileTool` |
| `session/__init__.py` | 创建 | 包标记 |
| `session/manager.py` | 创建（任务 5） | `Session` / `SessionManager` |
| `memory/__init__.py` | 创建 | 包标记 |
| `memory/loader.py` | 创建（任务 6） | `MemoryLoader` |
| `skills/__init__.py` | 创建 | 包标记 |
| `skills/loader.py` | 创建（任务 7） | `SkillsLoader` |
| `agent/__init__.py` | 创建 | 包标记 |
| `agent/context.py` | 创建（任务 8） | `ContextBuilder` |
| `agent/loop.py` | 创建（任务 8） | `AgentLoop` |
| `channels/__init__.py` | 创建 | 包标记 |
| `channels/base.py` | 创建（任务 9） | `BaseChannel` / `MessageBus` / 消息载体 |
| `channels/cli.py` | 创建（任务 9） | `CLIChannel` |
| `workspace/SOUL.md` | 创建（任务 1） | 默认人设模板 |
| `workspace/AGENTS.md` | 创建（任务 1） | 默认 Agent 行为指引 |
| `workspace/USER.md` | 创建（任务 1） | 默认用户档案 |
| `workspace/memory/MEMORY.md` | 创建（任务 1） | 默认长期记忆 |
| `tests/__init__.py` | 创建（任务 4 首次需要时） | 包标记 |
| `tests/test_tools.py` | 创建（任务 4） | 工具系统测试 |
| `tests/test_session.py` | 创建（任务 5） | 会话测试 |
| `tests/test_memory_loader.py` | 创建（任务 6） | memory 测试 |
| `tests/test_skills_loader.py` | 创建（任务 7） | skills 测试 |
| `tests/test_context_builder.py` | 创建（任务 8） | ContextBuilder 测试 |
| `tests/test_message_bus.py` | 创建（任务 9） | 消息总线测试 |
| `agent-tool.py` / `agent-memory.py` / `agent-gateway.py` / `skills-loader.py` | git add（任务 1，脱敏后）→ git rm（任务 11） | 旧快照，从代码起点逐步替换 |

---

## 任务 1：项目骨架，纳入现有快照代码

**文件：**
- 修改：`agent-tool.py:14`（脱敏 API key）
- 创建：`pyproject.toml`、`.env.example`、`README.md`、`workspace/SOUL.md`、`workspace/AGENTS.md`、`workspace/USER.md`、`workspace/memory/MEMORY.md`

- [ ] **步骤 1.1：脱敏 `agent-tool.py` 第 14 行**

把第 14 行的真实 OpenRouter key 替换为占位符（与另外两份快照保持一致）：

```python
API_KEY = "sk-or-v1-你的密钥"
```

运行：`grep -n "sk-or-v1-fe549" agent-tool.py`
预期：无输出（已脱敏）。

- [ ] **步骤 1.2：创建 `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "picobot"
version = "0.1.0"
description = "A minimal nanobot-inspired agent — picobot"
requires-python = ">=3.10"
dependencies = [
    "openai>=1.0",
]

[project.optional-dependencies]
dotenv = ["python-dotenv>=1.0"]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.23",
]

[tool.setuptools]
py-modules = ["app", "config"]
packages = [
    "agent",
    "channels",
    "memory",
    "providers",
    "session",
    "skills",
    "tools",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **步骤 1.3：创建 `.env.example`**

```
# 必填：你的 LLM API 凭证（参考 OpenAI 兼容端点格式）
API_KEY=
API_BASE=https://api.openai.com/v1
MODEL=gpt-4o-mini

# 可选：自定义 workspace 目录（留空使用 ~/.picobot/workspace）
# WORKSPACE=

# 可选：调整 Agent 行为（留空使用默认值）
# MAX_ITERATIONS=10
# HISTORY_LIMIT=50
```

注意：`API_KEY=` 后面必须留空，避免 grep 误命中 `sk-or-` 之类模式。

- [ ] **步骤 1.4：创建 `README.md` 初稿**

```markdown
# Picobot

参考 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 的极简 Agent 实现。

详细设计见 [docs/superpowers/specs/2026-05-10-picobot-restructure-design.md](docs/superpowers/specs/2026-05-10-picobot-restructure-design.md)。

> 项目正在拆分中，完整运行指南将在最后一步补齐。
```

- [ ] **步骤 1.5：创建 workspace 模板文件**

`workspace/SOUL.md`：
```markdown
# Soul

我是 Picobot，一个有帮助的 AI 助手。

友善、简洁、准确。
```

`workspace/AGENTS.md`：
```markdown
# Agent Instructions

- 先说意图，再调工具
- 修改文件前先读取
- 不确定时主动询问
```

`workspace/USER.md`：
```markdown
# User Profile

（请编辑此文件来告诉 Bot 你的信息）
```

`workspace/memory/MEMORY.md`：
```markdown
# Memory

（这里是长期记忆，由你或 Bot 编辑维护）
```

- [ ] **步骤 1.6：验证 .gitignore 已正确隔离敏感文件**

运行：`git check-ignore -v .env 2>&1; git check-ignore -v .venv 2>&1`
预期：两条都返回 `.gitignore:行号:模式  路径`（说明被忽略）。如果有 `.env` 文件存在不会被提交。

- [ ] **步骤 1.7：git add + commit**

```bash
git add agent-tool.py agent-memory.py agent-gateway.py skills-loader.py \
        pyproject.toml .env.example README.md workspace/
git status   # 检查没有遗漏文件
git commit -m "$(cat <<'EOF'
chore: 初始化项目骨架，纳入现有快照代码

- 添加 pyproject.toml、.env.example、workspace 模板、README 初稿
- 把现有 mini-agent 快照（agent-tool / agent-memory / agent-gateway / skills-loader）
  脱敏后纳入 git，作为重构起点；后续会拆分到各模块并在 commit 11 移除
EOF
)"
```

---

## 任务 2：Config 模块

**文件：**
- 创建：`config.py`

- [ ] **步骤 2.1：创建 `config.py`**

```python
"""Picobot 配置加载。

从环境变量（可选 .env）读取，提供统一默认值。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_if_present() -> None:
    """尝试加载 .env；python-dotenv 未安装则静默跳过。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


@dataclass(frozen=True)
class Config:
    api_base: str
    api_key: str
    model: str
    workspace: Path
    max_iterations: int = 10
    history_limit: int = 50

    @classmethod
    def from_env(cls) -> "Config":
        _load_dotenv_if_present()
        api_key = os.environ.get("API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "API_KEY 未设置。请配置环境变量或 .env 文件（参考 .env.example）。"
            )
        workspace_str = os.environ.get("WORKSPACE", "").strip()
        workspace = (
            Path(workspace_str).expanduser()
            if workspace_str
            else Path("~/.picobot/workspace").expanduser()
        )
        return cls(
            api_base=os.environ.get("API_BASE", "https://api.openai.com/v1"),
            api_key=api_key,
            model=os.environ.get("MODEL", "gpt-4o-mini"),
            workspace=workspace,
            max_iterations=int(os.environ.get("MAX_ITERATIONS", "10")),
            history_limit=int(os.environ.get("HISTORY_LIMIT", "50")),
        )
```

- [ ] **步骤 2.2：smoke 验证可导入**

运行：`python -c "from config import Config; print(Config.__name__)"`
预期：输出 `Config`，无报错。

- [ ] **步骤 2.3：git add + commit**

```bash
git add config.py
git commit -m "feat(config): 引入 Config 与环境变量加载"
```

---

## 任务 3：Provider 抽象与 OpenAI 实现

**文件：**
- 创建：`providers/__init__.py`、`providers/base.py`、`providers/openai.py`

- [ ] **步骤 3.1：创建 `providers/__init__.py`**

```python
"""Provider 抽象层。"""
```

- [ ] **步骤 3.2：创建 `providers/base.py`**

```python
"""Provider 抽象接口。

把 LLM SDK 锁在 provider 实现里，AgentLoop 只面向 Provider 编程。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON string，由 AgentLoop 调 json.loads 反序列化


@dataclass
class ProviderResponse:
    content: str | None
    tool_calls: list[ToolCall]


class Provider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> ProviderResponse:
        """与 LLM 对话一轮。"""
```

- [ ] **步骤 3.3：创建 `providers/openai.py`**

```python
"""OpenAI 兼容 Provider 实现。

支持任何 OpenAI 兼容端点（OpenAI、OpenRouter、本地 Ollama 等）。
"""
from __future__ import annotations

import asyncio

from openai import OpenAI

from providers.base import Provider, ProviderResponse, ToolCall


class OpenAIProvider(Provider):
    def __init__(
        self,
        api_base: str,
        api_key: str,
        model: str,
        temperature: float = 0.1,
    ):
        self._client = OpenAI(base_url=api_base, api_key=api_key)
        self._model = model
        self._temperature = temperature

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> ProviderResponse:
        # OpenAI Python SDK 是同步的；放到默认线程池避免阻塞事件循环
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._model,
            messages=messages,
            tools=tools or None,
            temperature=self._temperature,
        )
        message = response.choices[0].message
        tool_calls: list[ToolCall] = []
        if message.tool_calls:
            for call in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=call.id,
                        name=call.function.name,
                        arguments=call.function.arguments,
                    )
                )
        return ProviderResponse(content=message.content, tool_calls=tool_calls)
```

- [ ] **步骤 3.4：smoke 验证可导入**

运行：`python -c "from providers.base import Provider, ProviderResponse, ToolCall; from providers.openai import OpenAIProvider; print('OK')"`
预期：输出 `OK`。

- [ ] **步骤 3.5：git add + commit**

```bash
git add providers/
git commit -m "feat(providers): 抽象 Provider 接口与 OpenAI 实现"
```

---

## 任务 4：Tools 系统（TDD）

**文件：**
- 创建：`tests/__init__.py`、`tests/test_tools.py`、`tools/__init__.py`、`tools/base.py`、`tools/exec.py`、`tools/files.py`

- [ ] **步骤 4.1：安装开发依赖（一次性）**

运行：`pip install -e ".[dev,dotenv]"`
预期：成功安装 `openai`、`python-dotenv`、`pytest`、`pytest-asyncio`。后续任务都依赖此环境。

- [ ] **步骤 4.2：创建 `tests/__init__.py`**

空文件即可。

- [ ] **步骤 4.3：编写失败的测试 `tests/test_tools.py`**

```python
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
```

- [ ] **步骤 4.4：运行测试验证失败**

运行：`pytest tests/test_tools.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'tools'`（或类似导入错）。

- [ ] **步骤 4.5：创建 `tools/__init__.py`**

```python
"""工具系统。"""
```

- [ ] **步骤 4.6：创建 `tools/base.py`**

```python
"""Tool 抽象与注册表。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]: ...

    @abstractmethod
    async def execute(self, **kwargs) -> str: ...

    def to_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict]:
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Unknown tool '{name}'"
        try:
            return await tool.execute(**params)
        except Exception as exc:
            return f"Error: {exc}"
```

- [ ] **步骤 4.7：创建 `tools/exec.py`**

```python
"""执行 shell 命令的工具。"""
from __future__ import annotations

import asyncio

from tools.base import Tool

DANGEROUS_PATTERNS = ["rm -rf", "mkfs", "dd if=", "shutdown"]


class ExecTool(Tool):
    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute a shell command."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command"},
            },
            "required": ["command"],
        }

    async def execute(self, command: str, **kwargs) -> str:
        lowered = command.lower()
        for bad in DANGEROUS_PATTERNS:
            if bad in lowered:
                return f"Error: Blocked ({bad})"
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
            result = out.decode(errors="replace")
            if err:
                result += f"\nSTDERR:\n{err.decode(errors='replace')}"
            return (result or "(no output)")[:10000]
        except Exception as exc:
            return f"Error: {exc}"
```

- [ ] **步骤 4.8：创建 `tools/files.py`**

```python
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
```

- [ ] **步骤 4.9：运行测试验证全部通过**

运行：`pytest tests/test_tools.py -v`
预期：6 个 case 全 PASS。

- [ ] **步骤 4.10：git add + commit**

```bash
git add tests/__init__.py tests/test_tools.py tools/
git commit -m "feat(tools): 拆分工具系统至 tools/ 目录（含测试）"
```

---

## 任务 5：Session 模块（TDD）

**文件：**
- 创建：`tests/test_session.py`、`session/__init__.py`、`session/manager.py`

- [ ] **步骤 5.1：编写失败的测试 `tests/test_session.py`**

```python
"""Session 模块单元测试。"""
from __future__ import annotations

from pathlib import Path

from session.manager import Session, SessionManager


def test_get_history_truncates_to_max_messages():
    session = Session(key="cli:direct")
    session.messages = [{"role": "user", "content": str(i)} for i in range(10)]
    history = session.get_history(max_messages=3)
    assert len(history) == 3
    assert history[0]["content"] == "7"


def test_get_history_aligns_to_first_user_role():
    session = Session(
        key="cli:direct",
        messages=[
            {"role": "tool", "tool_call_id": "x", "content": "tool result"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ],
    )
    history = session.get_history(max_messages=10)
    assert history[0]["role"] == "user"
    assert len(history) == 2


def test_session_manager_persists_and_reloads(tmp_path: Path):
    manager = SessionManager(tmp_path)
    session = manager.get_or_create("cli:direct")
    session.messages = [{"role": "user", "content": "你好"}]
    manager.save(session)

    fresh = SessionManager(tmp_path)
    reloaded = fresh.get_or_create("cli:direct")
    assert reloaded.messages == [{"role": "user", "content": "你好"}]


def test_session_manager_caches_in_memory(tmp_path: Path):
    manager = SessionManager(tmp_path)
    a = manager.get_or_create("cli:direct")
    b = manager.get_or_create("cli:direct")
    assert a is b


def test_session_key_with_colon_safely_persisted(tmp_path: Path):
    manager = SessionManager(tmp_path)
    session = manager.get_or_create("telegram:1234")
    session.messages = [{"role": "user", "content": "x"}]
    manager.save(session)
    files = list((tmp_path / "sessions").iterdir())
    assert all(":" not in f.name for f in files)
    assert any("telegram_1234" in f.name for f in files)
```

- [ ] **步骤 5.2：运行测试验证失败**

运行：`pytest tests/test_session.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'session'`。

- [ ] **步骤 5.3：创建 `session/__init__.py`**

```python
"""会话历史管理。"""
```

- [ ] **步骤 5.4：创建 `session/manager.py`**

```python
"""会话历史管理。

每个会话以 jsonl 形式持久化到 sessions/ 子目录。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Session:
    key: str
    messages: list[dict] = field(default_factory=list)

    def get_history(self, max_messages: int = 50) -> list[dict]:
        recent = self.messages[-max_messages:]
        for index, message in enumerate(recent):
            if message.get("role") == "user":
                return recent[index:]
        return recent


class SessionManager:
    def __init__(self, workspace: Path):
        self.dir = Path(workspace) / "sessions"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        if key in self._cache:
            return self._cache[key]
        session = self._load(key) or Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session) -> None:
        path = self._path_for(session.key)
        with open(path, "w", encoding="utf-8") as handle:
            for message in session.messages:
                handle.write(json.dumps(message, ensure_ascii=False) + "\n")

    def _load(self, key: str) -> Session | None:
        path = self._path_for(key)
        if not path.exists():
            return None
        messages = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return Session(key=key, messages=messages)

    def _path_for(self, key: str) -> Path:
        safe = key.replace(":", "_")
        return self.dir / f"{safe}.jsonl"
```

- [ ] **步骤 5.5：运行测试验证全部通过**

运行：`pytest tests/test_session.py -v`
预期：5 个 case 全 PASS。

- [ ] **步骤 5.6：git add + commit**

```bash
git add tests/test_session.py session/
git commit -m "feat(session): 迁移会话管理至 session/ 目录（含测试）"
```

---

## 任务 6：Memory 模块（TDD）

**文件：**
- 创建：`tests/test_memory_loader.py`、`memory/__init__.py`、`memory/loader.py`

- [ ] **步骤 6.1：编写失败的测试 `tests/test_memory_loader.py`**

```python
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
```

- [ ] **步骤 6.2：运行测试验证失败**

运行：`pytest tests/test_memory_loader.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'memory'`。

- [ ] **步骤 6.3：创建 `memory/__init__.py`**

```python
"""长期记忆加载（只读）。"""
```

- [ ] **步骤 6.4：创建 `memory/loader.py`**

```python
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
```

- [ ] **步骤 6.5：运行测试验证全部通过**

运行：`pytest tests/test_memory_loader.py -v`
预期：3 个 case 全 PASS。

- [ ] **步骤 6.6：git add + commit**

```bash
git add tests/test_memory_loader.py memory/
git commit -m "feat(memory): 提取 MemoryLoader 模块（含测试）"
```

---

## 任务 7：Skills 模块（TDD）

**文件：**
- 创建：`tests/test_skills_loader.py`、`skills/__init__.py`、`skills/loader.py`

- [ ] **步骤 7.1：编写失败的测试 `tests/test_skills_loader.py`**

```python
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
```

- [ ] **步骤 7.2：运行测试验证失败**

运行：`pytest tests/test_skills_loader.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'skills'`。

- [ ] **步骤 7.3：创建 `skills/__init__.py`**

```python
"""Skills 索引加载。"""
```

- [ ] **步骤 7.4：创建 `skills/loader.py`**

```python
"""Skills 索引加载器。

扫描 workspace/skills 与可选的内置目录，输出可注入到 system prompt 的 XML 片段。
"""
from __future__ import annotations

import re
from pathlib import Path


class SkillsLoader:
    def __init__(self, workspace: Path, builtin_dir: Path | None = None):
        self.workspace_skills = Path(workspace) / "skills"
        self.builtin_skills = builtin_dir

    def list_skills(self) -> list[dict]:
        skills: list[dict] = []
        if self.workspace_skills.exists():
            for directory in self.workspace_skills.iterdir():
                skill_file = directory / "SKILL.md"
                if directory.is_dir() and skill_file.exists():
                    skills.append(
                        {
                            "name": directory.name,
                            "path": str(skill_file),
                            "description": self._get_description(skill_file),
                        }
                    )
        if self.builtin_skills and self.builtin_skills.exists():
            existing = {skill["name"] for skill in skills}
            for directory in self.builtin_skills.iterdir():
                skill_file = directory / "SKILL.md"
                if (
                    directory.is_dir()
                    and skill_file.exists()
                    and directory.name not in existing
                ):
                    skills.append(
                        {
                            "name": directory.name,
                            "path": str(skill_file),
                            "description": self._get_description(skill_file),
                        }
                    )
        return skills

    def build_skills_summary(self) -> str:
        skills = self.list_skills()
        if not skills:
            return ""
        lines = ["<skills>"]
        for skill in skills:
            lines.append("  <skill>")
            lines.append(f"    <name>{skill['name']}</name>")
            lines.append(f"    <description>{skill['description']}</description>")
            lines.append(f"    <location>{skill['path']}</location>")
            lines.append("  </skill>")
        lines.append("</skills>")
        return "\n".join(lines)

    def _get_description(self, path: Path) -> str:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                for line in match.group(1).split("\n"):
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
        return path.parent.name
```

- [ ] **步骤 7.5：运行测试验证全部通过**

运行：`pytest tests/test_skills_loader.py -v`
预期：5 个 case 全 PASS。

- [ ] **步骤 7.6：git add + commit**

```bash
git add tests/test_skills_loader.py skills/
git commit -m "feat(skills): 接入 SkillsLoader 与 skills/ 目录（含测试）"
```

---

## 任务 8：Agent 模块（ContextBuilder TDD + AgentLoop）

**文件：**
- 创建：`tests/test_context_builder.py`、`agent/__init__.py`、`agent/context.py`、`agent/loop.py`

- [ ] **步骤 8.1：编写失败的测试 `tests/test_context_builder.py`**

```python
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
```

- [ ] **步骤 8.2：运行测试验证失败**

运行：`pytest tests/test_context_builder.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'agent'`。

- [ ] **步骤 8.3：创建 `agent/__init__.py`**

```python
"""Agent 核心。"""
```

- [ ] **步骤 8.4：创建 `agent/context.py`**

```python
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
```

- [ ] **步骤 8.5：运行测试验证全部通过**

运行：`pytest tests/test_context_builder.py -v`
预期：6 个 case 全 PASS。

- [ ] **步骤 8.6：创建 `agent/loop.py`**

`AgentLoop` 不写测试（依赖 LLM；规格已说明）。

```python
"""ReAct 循环。

消费 inbound 消息 → 调 provider → 派工具 → 发 outbound。
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime

from agent.context import ContextBuilder
from channels.base import MessageBus, OutboundMessage
from providers.base import Provider
from session.manager import SessionManager
from tools.base import ToolRegistry


class AgentLoop:
    def __init__(
        self,
        bus: MessageBus,
        provider: Provider,
        tools: ToolRegistry,
        context: ContextBuilder,
        sessions: SessionManager,
        max_iterations: int = 10,
        history_limit: int = 50,
    ):
        self._bus = bus
        self._provider = provider
        self._tools = tools
        self._context = context
        self._sessions = sessions
        self._max_iterations = max_iterations
        self._history_limit = history_limit

    async def run(self) -> None:
        while True:
            try:
                message = await asyncio.wait_for(self._bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            session = self._sessions.get_or_create(message.session_key)
            history = session.get_history(max_messages=self._history_limit)
            messages = self._context.build_messages(history, message.content)
            reply = await self._react(messages)

            timestamp = datetime.now().isoformat()
            session.messages.append(
                {"role": "user", "content": message.content, "timestamp": timestamp}
            )
            session.messages.append(
                {"role": "assistant", "content": reply, "timestamp": timestamp}
            )
            self._sessions.save(session)

            await self._bus.publish_outbound(
                OutboundMessage(
                    channel=message.channel,
                    chat_id=message.chat_id,
                    content=reply,
                )
            )

    async def _react(self, messages: list[dict]) -> str:
        for _ in range(self._max_iterations):
            response = await self._provider.chat(
                messages, tools=self._tools.get_definitions() or None
            )
            if response.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.name,
                                    "arguments": call.arguments,
                                },
                            }
                            for call in response.tool_calls
                        ],
                    }
                )
                for call in response.tool_calls:
                    args = json.loads(call.arguments)
                    print(f"  [Tool] {call.name}({call.arguments[:80]})")
                    result = await self._tools.execute(call.name, args)
                    messages.append(
                        {"role": "tool", "tool_call_id": call.id, "content": result}
                    )
            else:
                return response.content or ""
        return "Max iterations reached."
```

注意：`agent/loop.py` 引用了 `channels/base.py` 中的 `MessageBus` 与 `OutboundMessage`。这两个类将在任务 9 创建。在任务 8 commit 前，import 暂时无法解析。

**应对方式：** 任务 8 的 commit 暂不验证 `agent/loop.py` 的运行时可导入；只确保 `agent/context.py` 的测试通过。完整 import 链将在任务 9 完成后由任务 10 的 smoke test 验证。

- [ ] **步骤 8.7：smoke 验证 `agent.context` 可独立导入**

运行：`python -c "from agent.context import ContextBuilder; print('OK')"`
预期：输出 `OK`（不导入 `agent.loop`，避免触发尚未创建的 `channels.base`）。

- [ ] **步骤 8.8：git add + commit**

```bash
git add tests/test_context_builder.py agent/
git commit -m "feat(agent): 落地 ContextBuilder 与 AgentLoop（含 ContextBuilder 测试）"
```

---

## 任务 9：Channels 模块（MessageBus TDD + CLI）

**文件：**
- 创建：`tests/test_message_bus.py`、`channels/__init__.py`、`channels/base.py`、`channels/cli.py`

- [ ] **步骤 9.1：编写失败的测试 `tests/test_message_bus.py`**

```python
"""MessageBus 与 Channel 元素的单元测试。"""
from __future__ import annotations

import asyncio

import pytest

from channels.base import InboundMessage, MessageBus, OutboundMessage


def test_inbound_session_key_format():
    msg = InboundMessage(channel="cli", sender_id="user", chat_id="direct", content="x")
    assert msg.session_key == "cli:direct"


@pytest.mark.asyncio
async def test_publish_and_consume_inbound_roundtrip():
    bus = MessageBus()
    sent = InboundMessage(channel="cli", sender_id="user", chat_id="direct", content="hi")
    await bus.publish_inbound(sent)
    received = await asyncio.wait_for(bus.consume_inbound(), timeout=1.0)
    assert received is sent


@pytest.mark.asyncio
async def test_publish_and_consume_outbound_roundtrip():
    bus = MessageBus()
    sent = OutboundMessage(channel="cli", chat_id="direct", content="ok")
    await bus.publish_outbound(sent)
    received = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
    assert received is sent


@pytest.mark.asyncio
async def test_inbound_and_outbound_queues_are_independent():
    bus = MessageBus()
    inbound_msg = InboundMessage(channel="cli", sender_id="user", chat_id="direct", content="i")
    outbound_msg = OutboundMessage(channel="cli", chat_id="direct", content="o")
    await bus.publish_inbound(inbound_msg)
    await bus.publish_outbound(outbound_msg)
    assert (await asyncio.wait_for(bus.consume_inbound(), timeout=1.0)) is inbound_msg
    assert (await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)) is outbound_msg
```

- [ ] **步骤 9.2：运行测试验证失败**

运行：`pytest tests/test_message_bus.py -v`
预期：FAIL，报错 `ModuleNotFoundError: No module named 'channels'`。

- [ ] **步骤 9.3：创建 `channels/__init__.py`**

```python
"""接入渠道与消息总线。"""
```

- [ ] **步骤 9.4：创建 `channels/base.py`**

```python
"""消息总线、消息载体与 Channel 抽象。"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class InboundMessage:
    channel: str
    sender_id: str
    chat_id: str
    content: str

    @property
    def session_key(self) -> str:
        return f"{self.channel}:{self.chat_id}"


@dataclass
class OutboundMessage:
    channel: str
    chat_id: str
    content: str


class MessageBus:
    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()

    async def publish_inbound(self, message: InboundMessage) -> None:
        await self.inbound.put(message)

    async def consume_inbound(self) -> InboundMessage:
        return await self.inbound.get()

    async def publish_outbound(self, message: OutboundMessage) -> None:
        await self.outbound.put(message)

    async def consume_outbound(self) -> OutboundMessage:
        return await self.outbound.get()


class BaseChannel(ABC):
    name: str = "base"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None: ...

    async def handle_message(self, sender_id: str, chat_id: str, content: str) -> None:
        await self.bus.publish_inbound(
            InboundMessage(
                channel=self.name,
                sender_id=sender_id,
                chat_id=chat_id,
                content=content,
            )
        )
```

- [ ] **步骤 9.5：创建 `channels/cli.py`**

```python
"""CLI Channel 实现。"""
from __future__ import annotations

import asyncio

from channels.base import BaseChannel, OutboundMessage


class CLIChannel(BaseChannel):
    name = "cli"

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            await self.handle_message("user", "direct", user_input)

    async def stop(self) -> None:
        return None

    async def send(self, message: OutboundMessage) -> None:
        print(f"\nBot: {message.content}\n")
```

- [ ] **步骤 9.6：运行 message bus 测试验证通过**

运行：`pytest tests/test_message_bus.py -v`
预期：4 个 case 全 PASS。

- [ ] **步骤 9.7：smoke 验证 `agent.loop` 现在能完整导入**

运行：`python -c "from agent.loop import AgentLoop; print('OK')"`
预期：输出 `OK`（任务 8 留下的 import 链已闭合）。

- [ ] **步骤 9.8：跑全量测试确认无回归**

运行：`pytest -v`
预期：到此累计 6 + 5 + 3 + 5 + 6 + 4 = 29 个 case 全 PASS。

- [ ] **步骤 9.9：git add + commit**

```bash
git add tests/test_message_bus.py channels/
git commit -m "feat(channels): 拆分消息总线与 CLI 渠道（含 MessageBus 测试）"
```

---

## 任务 10：装配入口 `app.py`

**文件：**
- 创建：`app.py`

- [ ] **步骤 10.1：创建 `app.py`**

```python
"""Picobot 装配入口。

从 Config 加载配置 → 初始化 workspace 模板 → 实例化全部组件 → 启动 gateway。
"""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from agent.context import ContextBuilder
from agent.loop import AgentLoop
from channels.base import BaseChannel, MessageBus
from channels.cli import CLIChannel
from config import Config
from memory.loader import MemoryLoader
from providers.openai import OpenAIProvider
from session.manager import SessionManager
from skills.loader import SkillsLoader
from tools.base import ToolRegistry
from tools.exec import ExecTool
from tools.files import ReadFileTool, WriteFileTool

TEMPLATE_DIR = Path(__file__).parent / "workspace"


def init_workspace(workspace: Path) -> None:
    """首次启动时，把项目内 workspace/ 模板拷贝到运行时目录。

    已存在的文件不会被覆盖。
    """
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "memory").mkdir(exist_ok=True)
    if not TEMPLATE_DIR.exists():
        return
    for src in TEMPLATE_DIR.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE_DIR)
        dst = workspace / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


async def route_outbound(bus: MessageBus, channels: dict[str, BaseChannel]) -> None:
    while True:
        try:
            message = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        channel = channels.get(message.channel)
        if channel:
            await channel.send(message)


async def main() -> None:
    config = Config.from_env()
    init_workspace(config.workspace)

    bus = MessageBus()
    provider = OpenAIProvider(
        api_base=config.api_base,
        api_key=config.api_key,
        model=config.model,
    )

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    sessions = SessionManager(config.workspace)
    memory_loader = MemoryLoader(config.workspace)
    skills_loader = SkillsLoader(config.workspace)
    context = ContextBuilder(config.workspace, memory_loader, skills_loader)

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        tools=tools,
        context=context,
        sessions=sessions,
        max_iterations=config.max_iterations,
        history_limit=config.history_limit,
    )

    cli = CLIChannel(bus)
    channels: dict[str, BaseChannel] = {"cli": cli}

    print(f"Picobot 已启动。Workspace: {config.workspace}")
    print(f"Channels: {list(channels.keys())}\n输入 exit 退出\n")

    await asyncio.gather(
        agent.run(),
        route_outbound(bus, channels),
        *[channel.start() for channel in channels.values()],
    )


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **步骤 10.2：smoke 验证 import**

运行：`python -c "import app; print('OK')"`
预期：输出 `OK`，无 import 错。

- [ ] **步骤 10.3：smoke 验证 `init_workspace` 行为（不实际启动 main）**

运行：
```bash
python -c "
from pathlib import Path
import tempfile, shutil
from app import init_workspace, TEMPLATE_DIR
with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp) / 'ws'
    init_workspace(target)
    assert (target / 'SOUL.md').exists(), 'SOUL.md 未拷贝'
    assert (target / 'memory' / 'MEMORY.md').exists(), 'MEMORY.md 未拷贝'
    print('init_workspace OK，模板源:', TEMPLATE_DIR)
"
```
预期：输出 `init_workspace OK，模板源: ...workspace`，无 assert 报错。

- [ ] **步骤 10.4：跑全量测试确认无回归**

运行：`pytest -v`
预期：29 个 case 全 PASS。

- [ ] **步骤 10.5：git add + commit**

```bash
git add app.py
git commit -m "feat(app): 装配入口 app.py"
```

---

## 任务 11：删除旧快照

**文件：**
- 删除：`agent-tool.py`、`agent-memory.py`、`agent-gateway.py`、`skills-loader.py`

- [ ] **步骤 11.1：使用 git 删除 4 个旧快照文件**

运行：
```bash
git rm agent-tool.py agent-memory.py agent-gateway.py skills-loader.py
git status
```
预期：4 个文件标记为 `deleted`，工作目录其它部分干净。

- [ ] **步骤 11.2：验证项目根再无旧 .py**

运行：`ls *.py 2>&1 | grep -E "agent-(tool|memory|gateway)|skills-loader"`
预期：无输出（无匹配）。

PowerShell 等价：`Get-ChildItem -Filter "*.py" | Select-String -Pattern "agent-|skills-loader"`，预期空集。

- [ ] **步骤 11.3：再跑全量测试确认无回归**

运行：`pytest -v`
预期：29 个 case 全 PASS。

- [ ] **步骤 11.4：commit**

```bash
git commit -m "$(cat <<'EOF'
chore: 删除旧快照（agent-tool/agent-memory/agent-gateway/skills-loader）

各模块已分别落地到 agent/ tools/ session/ memory/ skills/ channels/ providers/
对应包中。原 mini-agent 教学快照不再需要，从仓库移除。
EOF
)"
```

---

## 任务 12：完善 README

**文件：**
- 修改：`README.md`（覆盖任务 1 的初稿）

- [ ] **步骤 12.1：重写 `README.md`**

````markdown
# Picobot

参考 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 的极简 Agent 实现。

## 目录结构

```
picobot/
├── app.py                 # 装配入口
├── config.py              # 配置加载
├── providers/             # LLM provider 抽象
├── tools/                 # 工具系统（exec / read_file / write_file）
├── session/               # 会话历史管理
├── memory/                # 长期记忆加载（只读）
├── agent/                 # ReAct 循环 + system prompt 构造
├── channels/              # 接入渠道与消息总线（CLI）
├── skills/                # 技能索引加载
├── workspace/             # 默认 workspace 模板
└── tests/                 # 核心单元测试（pytest）
```

## 安装

```bash
pip install -e ".[dev,dotenv]"
```

`dev` 含测试依赖，`dotenv` 启用 `.env` 自动加载（推荐）。

## 配置

复制 `.env.example` 为 `.env` 并填写：

| 变量 | 必填 | 说明 |
|---|---|---|
| `API_KEY` | ✓ | LLM API key |
| `API_BASE` | | OpenAI 兼容端点（默认 `https://api.openai.com/v1`） |
| `MODEL` | | 模型名（默认 `gpt-4o-mini`） |
| `WORKSPACE` | | 自定义 workspace 路径（默认 `~/.picobot/workspace`） |
| `MAX_ITERATIONS` | | ReAct 最大轮次（默认 10） |
| `HISTORY_LIMIT` | | 单次注入的历史消息上限（默认 50） |

首次启动会把项目内 `workspace/` 模板拷贝到 `~/.picobot/workspace`（或你指定的路径）。

## 运行

```bash
python app.py
```

输入 `exit` 或 `quit` 退出。

## 测试

```bash
pytest -v
```

## 致谢

灵感与设计借鉴自 [HKUDS/nanobot](https://github.com/HKUDS/nanobot)。
````

- [ ] **步骤 12.2：把 README 渲染检查一遍**

运行：`cat README.md`（PowerShell 用 `Get-Content README.md`）
预期：标题、目录结构、表格、代码块都正确，没有未转义的反引号。

- [ ] **步骤 12.3：跑全量测试与 import smoke 做最终验收**

运行：
```bash
pytest -v
python -c "import app; print('app OK')"
```
预期：29 个 case 全 PASS，import smoke 输出 `app OK`。

- [ ] **步骤 12.4：验收清单逐项核查**

按规格第 10 节逐项确认：

```bash
# 1. commit 数量
git log --oneline | wc -l   # 预期 15（3 docs：规格 + 自检修订 + 计划；12 实现）

# 2. 没有 sk-or- 残留
git ls-files | xargs grep -l "sk-or-" 2>/dev/null   # 预期空

# 3. .env 不在 tracked，.env.example 在
git ls-files .env 2>&1                              # 预期空
git ls-files .env.example                           # 预期输出 .env.example

# 4. 旧快照已彻底移除
git ls-files | grep -E "agent-(tool|memory|gateway)|skills-loader"   # 预期空
```

PowerShell 等价：
```powershell
(git log --oneline | Measure-Object -Line).Lines
git ls-files | ForEach-Object { Select-String -Path $_ -Pattern "sk-or-" -Quiet | Where-Object { $_ } }
git ls-files .env
git ls-files .env.example
git ls-files | Select-String "agent-|skills-loader"
```

- [ ] **步骤 12.5：commit**

```bash
git add README.md
git commit -m "docs: 完善 README"
```

---

## 完成标准

按规格第 10 节，所有以下条件成立即视为完成：

1. `git log --oneline` 显示 15 个 commit（3 个 docs commit：规格 + 自检修订 + 计划；12 个实现 commit）。
2. `pytest -v` 全绿（29 个 case）。
3. `python app.py` 启动后 CLI 至少能完成一轮交互（前提：已配 `.env`，由用户手测）。
4. 项目根没有任何旧的 `agent-*.py` / `skills-loader.py`。
5. `git ls-files | xargs grep -l "sk-or-"` 无命中。
6. `.env` 不在 git tracked files 里；`.env.example` 在。
