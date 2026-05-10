"""Picobot 配置加载。

从环境变量（可选 .env）读取，提供统一默认值。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_if_present() -> None:
    """尝试加载 .env；python-dotenv 未安装则静默跳过。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


@dataclass(frozen=True)
class Config:
    api_base: str
    api_key: str
    model: str
    workspace: Path
    max_iterations: int = 10
    history_limit: int = 50

    @classmethod
    def from_env(cls) -> "Config":
        _load_dotenv_if_present()
        api_key = os.environ.get("API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "API_KEY 未设置。请配置环境变量或 .env 文件（参考 .env.example）。"
            )
        workspace_str = os.environ.get("WORKSPACE", "").strip()
        workspace = (
            Path(workspace_str).expanduser()
            if workspace_str
            else Path("~/.picobot/workspace").expanduser()
        )
        return cls(
            api_base=os.environ.get("API_BASE", "https://api.openai.com/v1"),
            api_key=api_key,
            model=os.environ.get("MODEL", "gpt-4o-mini"),
            workspace=workspace,
            max_iterations=int(os.environ.get("MAX_ITERATIONS", "10")),
            history_limit=int(os.environ.get("HISTORY_LIMIT", "50")),
        )
