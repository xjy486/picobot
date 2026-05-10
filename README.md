# Picobot

参考 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 的极简 Agent 实现。

## 目录结构

```
picobot/
├── app.py                 # 装配入口
├── config.py              # 配置加载
├── providers/             # LLM provider 抽象
├── tools/                 # 工具系统（exec / read_file / write_file）
├── session/               # 会话历史管理
├── memory/                # 长期记忆加载（只读）
├── agent/                 # ReAct 循环 + system prompt 构造
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

| 变量 | 必填 | 说明 |
|---|---|---|
| `API_KEY` | ✓ | LLM API key |
| `API_BASE` | | OpenAI 兼容端点（默认 `https://api.openai.com/v1`） |
| `MODEL` | | 模型名（默认 `gpt-4o-mini`） |
| `WORKSPACE` | | 自定义 workspace 路径（默认 `~/.picobot/workspace`） |
| `MAX_ITERATIONS` | | ReAct 最大轮次（默认 10） |
| `HISTORY_LIMIT` | | 单次注入的历史消息上限（默认 50） |

首次启动会把项目内 `workspace/` 模板拷贝到 `~/.picobot/workspace`（或你指定的路径）。

## 运行

```bash
python app.py
```

输入 `exit` 或 `quit` 退出。

## 测试

```bash
pytest -v
```

## 致谢

灵感与设计借鉴自 [HKUDS/nanobot](https://github.com/HKUDS/nanobot)。
