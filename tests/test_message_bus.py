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
