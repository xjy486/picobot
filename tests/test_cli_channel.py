"""CLIChannel 时序同步测试。

回归保护：避免下一轮 "You: " prompt 抢在 Bot 回复之前打印导致角色显示错乱。
"""
from __future__ import annotations

import asyncio
import threading

import pytest

from channels.base import MessageBus, OutboundMessage
from channels.cli import CLIChannel


@pytest.mark.asyncio
async def test_send_releases_ready_event():
    """send 完成后应释放 _ready，允许下一轮输入。"""
    bus = MessageBus()
    cli = CLIChannel(bus)

    assert cli._ready.is_set(), "初始状态应允许输入"

    cli._ready.clear()
    assert not cli._ready.is_set()

    await cli.send(OutboundMessage(channel="cli", chat_id="direct", content="hi"))
    assert cli._ready.is_set(), "send 后应允许下一轮输入"


@pytest.mark.asyncio
async def test_start_does_not_reprompt_before_reply(monkeypatch):
    """提交输入后到 Bot 回复前，不应再次调用 input(prompt)。"""
    bus = MessageBus()
    cli = CLIChannel(bus)

    input_calls: list[str] = []
    gate = threading.Event()
    user_inputs = iter(["hello", "exit"])

    def fake_input(prompt: str = "") -> str:
        input_calls.append(prompt)
        # 第二次 input 阻塞，直到测试主动放行
        if len(input_calls) >= 2:
            assert gate.wait(timeout=2.0), "测试未及时放行第二次输入"
        try:
            return next(user_inputs)
        except StopIteration as exc:
            raise EOFError from exc

    monkeypatch.setattr("builtins.input", fake_input)

    task = asyncio.create_task(cli.start())
    try:
        msg = await asyncio.wait_for(bus.consume_inbound(), timeout=2.0)
        assert msg.content == "hello"

        # Bot 回复之前给 channel 一点时间，确认它没立刻再次调用 input
        await asyncio.sleep(0.1)
        assert len(input_calls) == 1, (
            f"在 Bot 回复之前不应再次出现 You: prompt, 实际调用={input_calls}"
        )

        # 发送 Bot 回复
        await cli.send(OutboundMessage(channel="cli", chat_id="direct", content="hi back"))

        # 放行第二次 input 让 task 退出
        gate.set()
        await asyncio.wait_for(task, timeout=2.0)
    finally:
        gate.set()
        if not task.done():
            task.cancel()

    assert len(input_calls) == 2
