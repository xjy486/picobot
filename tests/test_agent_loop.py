"""AgentLoop 单元测试。"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent.context import ContextBuilder
from agent.loop import AgentLoop
from channels.base import MessageBus
from memory.loader import MemoryLoader
from providers.base import ProviderResponse, ToolCall
from session.manager import SessionManager
from skills.loader import SkillsLoader
from tools.base import Tool, ToolRegistry


class FakeTool(Tool):
    @property
    def name(self):
        return "noop"

    @property
    def description(self):
        return "does nothing"

    @property
    def parameters(self):
        return {"type": "object", "properties": {}}

    async def execute(self, **kwargs):
        return "ok"


class FakeProvider:
    def __init__(self, responses):
        self._responses = iter(responses)

    async def chat(self, messages, tools=None):
        return next(self._responses)


@pytest.fixture
def agent_deps(tmp_path: Path):
    bus = MessageBus()
    tools = ToolRegistry()
    tools.register(FakeTool())
    context = ContextBuilder(tmp_path, MemoryLoader(tmp_path), SkillsLoader(tmp_path))
    sessions = SessionManager(tmp_path)
    return bus, tools, context, sessions


@pytest.mark.asyncio
async def test_react_preserves_reasoning_content(agent_deps):
    """当 Provider 返回 tool_calls 且携带 reasoning_content 时，
    _react 应在回传的 assistant message 中包含该字段。"""
    bus, tools, context, sessions = agent_deps
    provider = FakeProvider([
        ProviderResponse(
            content=None,
            tool_calls=[ToolCall(id="c1", name="noop", arguments="{}")],
            reasoning_content="thinking about writing a file",
        ),
        ProviderResponse(content="done", tool_calls=[]),
    ])

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        tools=tools,
        context=context,
        sessions=sessions,
        max_iterations=5,
    )

    messages = [{"role": "user", "content": "write a file"}]
    reply = await agent._react(messages)

    assert reply == "done"
    # 第一轮的 assistant message 里应包含 reasoning_content
    assistant_msgs = [m for m in messages if m["role"] == "assistant"]
    assert len(assistant_msgs) == 1
    assert assistant_msgs[0].get("reasoning_content") == "thinking about writing a file"


@pytest.mark.asyncio
async def test_react_logs_debug_context(agent_deps):
    """当传入 debug_logger 时，_react 应在每次 provider.chat 前记录上下文。"""
    bus, tools, context, sessions = agent_deps
    provider = FakeProvider([
        ProviderResponse(
            content=None,
            tool_calls=[ToolCall(id="c1", name="noop", arguments="{}")],
        ),
        ProviderResponse(content="done", tool_calls=[]),
    ])

    logged = []

    class FakeDebugLogger:
        def __init__(self):
            self._enabled = True
        async def log_context(self, session_key, phase, messages):
            logged.append((session_key, phase, len(messages)))

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        tools=tools,
        context=context,
        sessions=sessions,
        max_iterations=5,
        debug_logger=FakeDebugLogger(),
    )

    messages = [{"role": "user", "content": "do something"}]
    reply = await agent._react(messages, session_key="cli:test")
    assert reply == "done"
    # 两次 provider.chat：第一次 tool_call + 第二次最终回复
    assert len(logged) == 2
    assert logged[0] == ("cli:test", "react_0", 1)
    assert logged[1] == ("cli:test", "react_1", 3)  # user + assistant + tool
