"""CLI Channel 实现。"""
from __future__ import annotations

import asyncio

from channels.base import BaseChannel, MessageBus, OutboundMessage


class CLIChannel(BaseChannel):
    name = "cli"

    def __init__(self, bus: MessageBus):
        super().__init__(bus)
        # 用户提交一次输入后 clear，等到对应 Bot 回复 send 完成才重新 set。
        # 防止 input("You: ") 抢在 Bot 输出之前打印导致两轮角色显示错乱。
        self._ready = asyncio.Event()
        self._ready.set()

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            await self._ready.wait()
            try:
                user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            except (EOFError, KeyboardInterrupt):
                return
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            self._ready.clear()
            await self.handle_message("user", "direct", user_input)

    async def stop(self) -> None:
        return None

    async def send(self, message: OutboundMessage) -> None:
        print(f"\nBot: {message.content}\n")
        self._ready.set()
