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
