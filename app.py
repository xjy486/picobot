"""Picobot 装配入口。

从 Config 加载配置 → 初始化 workspace 模板 → 实例化全部组件 → 启动 gateway。
"""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from agent.context import ContextBuilder
from agent.debug import DebugLogger
from agent.loop import AgentLoop
from channels.base import BaseChannel, MessageBus
from channels.cli import CLIChannel
from config import Config
from memory.loader import MemoryLoader
from providers.openai import OpenAIProvider
from session.manager import SessionManager
from skills.loader import SkillsLoader
from tools.base import ToolRegistry
from tools.exec import ExecTool
from tools.files import ReadFileTool, WriteFileTool

TEMPLATE_DIR = Path(__file__).parent / "workspace"


def init_workspace(workspace: Path) -> None:
    """首次启动时，把项目内 workspace/ 模板拷贝到运行时目录。

    已存在的文件不会被覆盖。
    """
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "memory").mkdir(exist_ok=True)
    if not TEMPLATE_DIR.exists():
        return
    for src in TEMPLATE_DIR.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE_DIR)
        dst = workspace / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


async def route_outbound(bus: MessageBus, channels: dict[str, BaseChannel]) -> None:
    while True:
        try:
            message = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        channel = channels.get(message.channel)
        if channel:
            await channel.send(message)


async def main() -> None:
    config = Config.from_env()
    init_workspace(config.workspace)

    bus = MessageBus()
    provider = OpenAIProvider(
        api_base=config.api_base,
        api_key=config.api_key,
        model=config.model,
    )

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    sessions = SessionManager(config.workspace)
    memory_loader = MemoryLoader(config.workspace)
    skills_loader = SkillsLoader(config.workspace)
    context = ContextBuilder(config.workspace, memory_loader, skills_loader)

    debug_logger = DebugLogger(config.workspace)
    if config.debug:
        debug_logger.enable(config.workspace)

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        tools=tools,
        context=context,
        sessions=sessions,
        max_iterations=config.max_iterations,
        history_limit=config.history_limit,
        debug_logger=debug_logger,
    )

    cli = CLIChannel(bus)
    channels: dict[str, BaseChannel] = {"cli": cli}

    print(f"Picobot 已启动。Workspace: {config.workspace}")
    print(f"Channels: {list(channels.keys())}\n输入 exit 退出\n")

    await asyncio.gather(
        agent.run(),
        route_outbound(bus, channels),
        *[channel.start() for channel in channels.values()],
    )


if __name__ == "__main__":
    asyncio.run(main())
