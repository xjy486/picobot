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
