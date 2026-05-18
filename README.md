# Picobot

参考 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 的极简 Agent 实现。

## 特性

- **ReAct 循环**：支持多轮 tool call，自动调用 exec / read_file / write_file 工具
- **OpenAI 兼容**：支持任何 OpenAI 兼容端点（OpenAI、OpenRouter、本地 Ollama、智谱、DeepSeek 等）
- **CLI 交互**：终端直接对话，输入 `exit` 退出
- **会话持久化**：自动保存对话历史到 workspace，支持跨会话上下文恢复
- **长期记忆**：自动加载 workspace/memory/MEMORY.md 作为长期记忆
- **调试日志**：调试模式下记录每轮对话完整上下文到 JSONL，便于排查 LLM 交互问题
- **thinking 模式兼容**：支持 reasoning / thinking 模型的多轮上下文回传

## 目录结构

```
picobot/
├── app.py                 # 装配入口
├── config.py              # 配置加载
├── providers/             # LLM provider 抽象
├── tools/                 # 工具系统（exec / read_file / write_file）
├── session/               # 会话历史管理（JSONL 持久化）
├── memory/                # 长期记忆加载（只读）
├── agent/                 # ReAct 循环 + system prompt 构造 + 调试日志
├── channels/              # 接入渠道与消息总线（CLI）
├── skills/                # 技能索引加载
├── workspace/             # 默认 workspace 模板
└── tests/                 # 核心单元测试（pytest）
```

## 安装

```bash
pip install -e ".[dev,dotenv]"
```

`dev` 含测试依赖（pytest、pytest-asyncio），`dotenv` 启用 `.env` 自动加载（推荐）。

## 配置

复制 `.env.example` 为 `.env` 并填写：

| 变量              | 必填 | 说明                                                 |
| ----------------- | ---- | ---------------------------------------------------- |
| `API_KEY`         | ✓    | LLM API key                                          |
| `API_BASE`        |      | OpenAI 兼容端点（默认 `https://api.openai.com/v1`）  |
| `MODEL`           |      | 模型名（默认 `gpt-4o-mini`）                         |
| `WORKSPACE`       |      | 自定义 workspace 路径（默认 `~/.picobot/workspace`） |
| `MAX_ITERATIONS`  |      | ReAct 最大轮次（默认 10）                            |
| `HISTORY_LIMIT`   |      | 单次注入的历史消息上限（默认 50）                    |
| `PICOBOT_DEBUG`   |      | 设为 `1` 启用调试日志（见下方说明）                  |

首次启动会把项目内 `workspace/` 模板拷贝到 `~/.picobot/workspace`（或你指定的路径）。

## 运行

```bash
python app.py
```

输入 `exit` 或 `quit` 退出。

## 调试模式

在 `.env` 中设置 `PICOBOT_DEBUG=1`，picobot 会在运行时自动在 `workspace/logs/` 下创建带时间戳的 JSONL 日志文件，记录每轮对话的完整上下文（system、user、assistant、tool call 等）。

日志示例（`workspace/logs/debug_20260518_143052.jsonl`）：

```jsonl
{"timestamp": "2026-05-18T14:30:52.123456", "session_key": "cli:direct", "phase": "start", "message_count": 5, "messages": [...]}
{"timestamp": "2026-05-18T14:30:53.234567", "session_key": "cli:direct", "phase": "react_0", "message_count": 7, "messages": [...]}
```

- `phase: "start"`：对话轮次开始时的完整上下文
- `phase: "react_N"`：ReAct 循环第 N 次调用 LLM 前的上下文快照

## 测试

```bash
pytest -v
```

## 致谢

灵感与设计借鉴自 [HKUDS/nanobot](https://github.com/HKUDS/nanobot)。
