"""CLI Channel 实现。"""
from __future__ import annotations

import asyncio

from channels.base import BaseChannel, OutboundMessage


class CLIChannel(BaseChannel):
    name = "cli"

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            try:
                user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            except (EOFError, KeyboardInterrupt):
                return
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            await self.handle_message("user", "direct", user_input)

    async def stop(self) -> None:
        return None

    async def send(self, message: OutboundMessage) -> None:
        print(f"\nBot: {message.content}\n")
