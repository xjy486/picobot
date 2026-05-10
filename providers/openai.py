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
