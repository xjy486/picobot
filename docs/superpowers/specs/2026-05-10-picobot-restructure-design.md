# Picobot 项目结构拆分设计

> 日期：2026-05-10
> 主题：将 picobot（nanobot 的极简实现）从单文件快照拆分为模块化包结构
> 参考：[HKUDS/nanobot](https://github.com/HKUDS/nanobot)

---

## 1. 背景

当前 `picobot/` 根目录下有 4 个 Python 文件：

- `agent-tool.py` / `agent-memory.py` / `agent-gateway.py`：**同一份代码的渐进式三层快照**，每一份包含上一份的内容，`agent-gateway.py` 是最完整版本（工具 + 会话 + 消息总线 + 多渠道）。
- `skills-loader.py`：独立的技能加载器。

存在的问题：

- 三份快照高度重复，没有清晰的模块边界。
- 不是 git 仓库，没有版本管理。
- `agent-tool.py` 第 14 行硬编码了真实的 API key。
- 所有职责（工具、会话、Provider、上下文、消息总线、渠道）挤在一个文件里，难以测试和扩展。

## 2. 目标

参考 nanobot 的架构思想，把现有代码拆分到一个清晰、模块化、可测试的包结构中。**保持极简**——不引入超过当前功能范围的扩展。

## 3. 已确认的设计决策

| # | 决策项 | 选择 | 理由 |
|---|---|---|---|
| 1 | 拆分基础 | 以 `agent-gateway.py` 为准，删除两份旧快照 | 旧快照只是教学过程的中间产物，全版本已涵盖其全部功能 |
| 2 | providers 抽象 | 抽象接口 + OpenAI 实现 | 把 SDK 锁在 provider 内，便于以后扩展，但当前不引入第二个 provider |
| 3 | memory 模块 | 只加载，不写入 | 维持极简定位，写入留给后续迭代 |
| 4 | workspace 目录 | 项目下的默认模板，运行时仍在 `~/.picobot/workspace` | 模板入库便于分发，运行数据不污染源码目录 |
| 5 | skills-loader.py 的处理 | 保留并接入，新增 `skills/` 一级目录 | 用户希望保留这部分能力 |
| 6 | 测试范围 | 核心单元测试（不测 LLM/IO 相关组件） | 单元测试快、稳定；ReAct 循环和 Provider 留给手测 |

## 4. 目标目录结构

```
picobot/
├── app.py                  # 装配入口：从 config 加载配置，组装组件，启动 gateway
├── config.py               # 配置加载（环境变量 + .env，统一默认值）
├── pyproject.toml          # 依赖与项目元数据
├── .env.example            # 环境变量模板（API_KEY/API_BASE/MODEL 等占位）
├── .gitignore              # 忽略 .env、__pycache__、.venv 等
├── README.md               # 项目说明 + 运行指南
│
├── providers/              # LLM provider 抽象
│   ├── __init__.py
│   ├── base.py             # Provider 抽象接口 + ProviderResponse
│   └── openai.py           # OpenAI 兼容实现
│
├── tools/                  # 工具系统
│   ├── __init__.py
│   ├── base.py             # Tool 抽象 + ToolRegistry
│   ├── exec.py             # ExecTool（含黑名单防护）
│   └── files.py            # ReadFileTool / WriteFileTool
│
├── session/                # 会话历史
│   ├── __init__.py
│   └── manager.py          # Session + SessionManager（jsonl 持久化）
│
├── memory/                 # 长期记忆加载（只读）
│   ├── __init__.py
│   └── loader.py           # 读取 workspace/memory/MEMORY.md 注入 prompt
│
├── agent/                  # Agent 核心
│   ├── __init__.py
│   ├── context.py          # ContextBuilder：拼装 system prompt
│   └── loop.py             # AgentLoop：ReAct 循环
│
├── channels/               # 接入渠道
│   ├── __init__.py
│   ├── base.py             # BaseChannel + InboundMessage / OutboundMessage / MessageBus
│   └── cli.py              # CLIChannel
│
├── skills/                 # 技能系统
│   ├── __init__.py
│   └── loader.py           # SkillsLoader
│
├── workspace/              # 默认 workspace 模板
│   ├── SOUL.md
│   ├── AGENTS.md
│   ├── USER.md
│   └── memory/
│       └── MEMORY.md
│
└── tests/                  # 核心单元测试
    ├── __init__.py
    ├── test_session.py
    ├── test_tools.py
    ├── test_memory_loader.py
    ├── test_context_builder.py
    ├── test_message_bus.py
    └── test_skills_loader.py
```

**依赖方向**：`channels → MessageBus ← AgentLoop → {Provider, ToolRegistry, ContextBuilder, SessionManager}`；`ContextBuilder → {memory.loader, skills.loader}`。**没有反向依赖**。

## 5. 关键接口设计

### 5.1 `providers/base.py`

```python
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str   # JSON string，由 AgentLoop 调 json.loads 反序列化


@dataclass
class ProviderResponse:
    content: str | None
    tool_calls: list[ToolCall]   # 没有工具调用时为空列表


class Provider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> ProviderResponse: ...
```

`AgentLoop` 只依赖 `Provider` 接口与 `ToolCall`，OpenAI SDK 的 `tool_calls` 结构由 `providers/openai.py` 转换为统一的 `ProviderResponse`。

### 5.2 `tools/base.py`

沿用现有 `Tool` 抽象与 `ToolRegistry`，三个具体 Tool 类拆到 `exec.py` / `files.py`。`ToolRegistry.execute(name, params)` 接口不变。

### 5.3 `session/manager.py`

`Session` + `SessionManager` 整体迁入，**不改变语义**：jsonl 持久化、按 session_key 缓存、按 user 角色找截断起点。

### 5.4 `memory/loader.py`

```python
class MemoryLoader:
    def __init__(self, workspace: Path): ...
    def load(self) -> str:
        """读取 workspace/memory/MEMORY.md，返回拼好的段落字符串；不存在或为空时返回空串。"""
```

### 5.5 `skills/loader.py`

现有 `SkillsLoader.build_skills_summary()` 迁入，签名不变。

### 5.6 `agent/context.py`

```python
class ContextBuilder:
    def __init__(
        self,
        workspace: Path,
        memory_loader: MemoryLoader,
        skills_loader: SkillsLoader | None = None,
    ): ...

    def build_system_prompt(self) -> str: ...   # 内部调用 memory_loader.load() 与 skills_loader.build_skills_summary()
    def build_messages(self, history: list[dict], user_message: str) -> list[dict]: ...
```

### 5.7 `agent/loop.py`

```python
class AgentLoop:
    def __init__(
        self,
        bus: MessageBus,
        provider: Provider,
        tools: ToolRegistry,
        context: ContextBuilder,
        sessions: SessionManager,
        max_iterations: int = 10,
    ): ...

    async def run(self): ...   # 消费 inbound → 调 provider → 派工具 → 发 outbound
```

与现有 `_react_loop` 唯一的差异是把 `client.chat.completions.create(...)` 替换为 `await self.provider.chat(...)`。

### 5.8 `channels/base.py`

`BaseChannel` + `InboundMessage` + `OutboundMessage` + `MessageBus` 整体迁入，语义不变。

### 5.9 `app.py`

≤ 60 行的装配入口。流程：

1. `Config.from_env()` 加载配置
2. 初始化 workspace 模板（首次启动从项目内 `workspace/` 拷贝到 `~/.picobot/workspace`）
3. 实例化 `provider` / `tools` / `sessions` / `memory_loader` / `skills_loader` / `context` / `bus` / `agent` / `cli_channel`
4. `asyncio.gather(agent.run(), route_outbound(...), cli_channel.start())`

## 6. 配置与依赖

### 6.1 `config.py`

```python
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
        load_dotenv_if_present()  # python-dotenv 不存在则跳过
        ...
```

默认 workspace：`~/.picobot/workspace`（与旧目录 `~/.mini-agent/workspace` 解耦）。

### 6.2 依赖管理

- 使用 `pyproject.toml`（PEP 621）。
- 运行依赖：`openai>=1.0`。
- 可选依赖（extras）：`dotenv = ["python-dotenv"]`。
- 开发依赖（extras）：`dev = ["pytest", "pytest-asyncio"]`。
- 安装命令：`pip install -e ".[dev,dotenv]"`。
- 不引入 poetry/uv 等额外工具。

### 6.3 安全处理

- **第一次 commit 之前**，必须从源码里删除所有真实 API key。
- `.env` 不入库，`.env.example` 入库。
- `.gitignore` 至少包含：`.env`、`.venv/`、`__pycache__/`、`*.egg-info/`、`.pytest_cache/`、`*.pyc`。
- 验收时 `grep 'sk-or-' .` 在 git tracked 文件中应无命中。

## 7. Git 工作流

约定式提交 + 中文描述。每一步独立 commit，便于 review：

```
1.  chore: 初始化项目骨架（git init、.gitignore、pyproject.toml、README）
2.  feat(config): 引入 Config 与环境变量加载
3.  feat(providers): 抽象 Provider 接口与 OpenAI 实现
4.  feat(tools): 拆分工具系统至 tools/ 目录
5.  feat(session): 迁移会话管理至 session/ 目录
6.  feat(memory): 提取 MemoryLoader 模块
7.  feat(skills): 接入 SkillsLoader 与 skills/ 目录
8.  feat(agent): 落地 ContextBuilder 与 AgentLoop
9.  feat(channels): 拆分消息总线与 CLI 渠道
10. feat(app): 装配入口 app.py
11. test: 补齐核心单元测试
12. chore: 删除旧快照（agent-tool/agent-memory/agent-gateway/skills-loader）
13. docs: 完善 README
```

## 8. 测试覆盖

使用 `pytest` + `pytest-asyncio`，每个测试文件 3-6 个 case：

| 测试文件 | 覆盖内容 |
|---|---|
| `test_session.py` | 历史截断、jsonl 持久化往返、按 user 角色定位起点 |
| `test_tools.py` | Tool schema 输出、ExecTool 黑名单拦截、ReadFileTool 不存在路径、WriteFileTool 父目录自动创建 |
| `test_memory_loader.py` | MEMORY.md 不存在 / 为空 / 有内容三种情况 |
| `test_context_builder.py` | bootstrap 文件存在与否的拼装顺序、skills 段落注入 |
| `test_message_bus.py` | inbound/outbound 队列收发、session_key 派生 |
| `test_skills_loader.py` | 工作区/内置 skills 合并、name 冲突去重、缺 description 时降级到目录名 |

**不测**：AgentLoop / Provider / CLIChannel（依赖真实 LLM 或 IO，留给手测）。

## 9. README.md 内容大纲

简短中文，包含：

1. 项目简介（一句话定位 + 致谢 nanobot）
2. 目录结构图
3. 安装：`pip install -e ".[dev,dotenv]"`
4. 配置：`.env` 字段说明（API_KEY / API_BASE / MODEL / WORKSPACE）
5. 运行：`python app.py`
6. 测试：`pytest`
7. 致谢：链接 nanobot

## 10. 验收标准

1. `git log --oneline` 显示 13 个干净的中文 commit（顺序与第 7 节一致）。
2. `pytest` 全绿。
3. `python app.py` 启动后 CLI 至少能完成一轮交互（前提：已配 `.env`）。
4. 项目根没有任何旧的 `agent-*.py` / `skills-loader.py`。
5. 源码里没有任何硬编码 API key（`grep 'sk-or-'` 在 git tracked 文件中无命中）。
6. `.env` 不在 git tracked files 里；`.env.example` 在。
