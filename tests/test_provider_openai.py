"""OpenAIProvider 单元测试。"""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from providers.openai import OpenAIProvider
from providers.base import ProviderResponse


@pytest.mark.asyncio
async def test_provider_extracts_reasoning_content(monkeypatch):
    """当服务端返回非标准 reasoning_content 字段时，ProviderResponse 应携带该字段。"""
    provider = OpenAIProvider(api_base="http://test", api_key="sk-test", model="test-model")

    # 构造 mock 响应：包含 reasoning_content
    mock_choice = MagicMock()
    mock_choice.message.content = "calling tool"
    mock_choice.message.tool_calls = None
    mock_choice.message.reasoning_content = "think before act"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    monkeypatch.setattr(provider, "_client", mock_client)

    resp = await provider.chat([{"role": "user", "content": "hi"}])
    assert isinstance(resp, ProviderResponse)
    assert resp.content == "calling tool"
    assert resp.reasoning_content == "think before act"


@pytest.mark.asyncio
async def test_provider_graceful_without_reasoning_content(monkeypatch):
    """标准 OpenAI 兼容端点不返回 reasoning_content 时，字段应为 None。"""
    provider = OpenAIProvider(api_base="http://test", api_key="sk-test", model="test-model")

    mock_choice = MagicMock()
    mock_choice.message.content = "hello"
    mock_choice.message.tool_calls = None
    mock_choice.message.reasoning_content = None
    mock_choice.message.model_extra = {}

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    monkeypatch.setattr(provider, "_client", mock_client)

    resp = await provider.chat([{"role": "user", "content": "hi"}])
    assert resp.reasoning_content is None
