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
