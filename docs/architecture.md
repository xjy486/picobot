# Picobot 系统架构

## 组件图

```mermaid
graph TB
    subgraph User["👤 用户"]
        CLI_IN["键盘输入"]
        CLI_OUT["终端输出"]
    end

    subgraph Channels["📡 channels/"]
        direction TB
        CLI["CLIChannel"]
        BUS["MessageBus<br/><i>inbound / outbound</i>"]
        BASE["BaseChannel<br/><i>抽象</i>"]
    end

    subgraph Agent["🧠 agent/"]
        LOOP["AgentLoop<br/><i>ReAct 循环</i>"]
        CTX["ContextBuilder<br/><i>System Prompt 拼装</i>"]
    end

    subgraph Provider["🔌 providers/"]
        P_BASE["Provider<br/><i>抽象接口</i>"]
        OPENAI["OpenAIProvider<br/><i>OpenAI 兼容实现</i>"]
    end

    subgraph Tools["🔧 tools/"]
        REG["ToolRegistry"]
        EXEC["ExecTool"]
        READ["ReadFileTool"]
        WRITE["WriteFileTool"]
    end

    subgraph Session["💾 session/"]
        SM["SessionManager<br/><i>jsonl 持久化</i>"]
        S["Session<br/><i>消息历史</i>"]
    end

    subgraph Memory["📝 memory/"]
        ML["MemoryLoader<br/><i>只读加载</i>"]
    end

    subgraph Skills["🛠️ skills/"]
        SKL["SkillsLoader<br/><i>XML 索引</i>"]
    end

    subgraph External["🌐 外部"]
        LLM["OpenRouter / OpenAI API"]
    end

    %% 消息流
    CLI_IN -->|"input()"| CLI
    CLI -->|"InboundMessage"| BUS
    BUS -->|"consume_inbound()"| LOOP
    LOOP -->|"build_messages()"| CTX
    CTX -->|"load()"| ML
    CTX -->|"build_skills_summary()"| SKL
    CTX -->|"get_history()"| SM
    LOOP -->|"chat(messages, tools)"| OPENAI
    OPENAI -->|"HTTP POST"| LLM
    LLM -->|"ProviderResponse"| OPENAI
    OPENAI -->|"content / tool_calls"| LOOP
    LOOP -->|"execute(name, args)"| REG
    REG --> EXEC
    REG --> READ
    REG --> WRITE
    LOOP -->|"save(session)"| SM
    SM -->|"jsonl 写入"| S
    LOOP -->|"OutboundMessage"| BUS
    BUS -->|"consume_outbound()"| CLI
    CLI -->|"print()"| CLI_OUT
```

## 核心流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant CLI as CLIChannel
    participant BUS as MessageBus
    participant AGENT as AgentLoop
    participant CTX as ContextBuilder
    participant P as OpenAIProvider
    participant T as ToolRegistry
    participant S as SessionManager

    U->>CLI: 输入消息
    CLI->>BUS: publish_inbound(InboundMessage)

    AGENT->>BUS: consume_inbound()
    BUS-->>AGENT: InboundMessage

    AGENT->>S: get_or_create(session_key)
    S-->>AGENT: Session + history

    AGENT->>CTX: build_messages(history, user_msg)
    CTX-->>AGENT: [system, *history, user]

    loop ReAct (最多 10 轮)
        AGENT->>P: chat(messages, tools)
        P-->>AGENT: ProviderResponse

        alt 有 tool_calls
            AGENT->>T: execute(name, args)
            T-->>AGENT: result
        else 无 tool_calls
            AGENT-->>AGENT: 退出循环
        end
    end

    AGENT->>S: save(session)
    AGENT->>BUS: publish_outbound(OutboundMessage)

    BUS-->>CLI: consume_outbound()
    CLI->>U: print(response)
```

## 依赖方向

```mermaid
graph LR
    APP["app.py"] --> CFG["config.py"]
    APP --> P["providers/"]
    APP --> T["tools/"]
    APP --> AG["agent/"]
    APP --> CH["channels/"]
    APP --> S["session/"]
    APP --> M["memory/"]
    APP --> SK["skills/"]

    AG --> P
    AG --> T
    AG --> CH
    AG --> S
    AG --> M
    AG --> SK

    CH -.-> AG

    style APP fill:#4a9eff,color:#fff
    style CFG fill:#6c757d,color:#fff
    style P fill:#28a745,color:#fff
    style T fill:#28a745,color:#fff
    style S fill:#28a745,color:#fff
    style M fill:#28a745,color:#fff
    style SK fill:#28a745,color:#fff
    style AG fill:#dc3545,color:#fff
    style CH fill:#ffc107
```

**规则：**
- 实线箭头 = 编译时 import 依赖
- 虚线箭头 = 运行时通过 MessageBus 间接通信
- 绿色 = 叶子模块（不被项目内其他模块依赖）
- 红色 = AgentLoop 是调度中枢，依赖几乎所有模块
- 黄色 = Channels 通过队列与 Agent 解耦，AgentLoop 只依赖 `channels.base` 中的 MessageBus/OutboundMessage

## 关键设计决策

| 决策 | 说明 |
|---|---|
| Provider 抽象 | `AgentLoop` 只依赖 `Provider` 接口，OpenAI SDK 锁在 `OpenAIProvider` 里，换模型只需新增一个实现 |
| MessageBus 解耦 | Channel 与 Agent 通过 `asyncio.Queue` 通信，互不感知。加 Telegram/Discord 只需实现 `BaseChannel` |
| ContextBuilder 注入 | `MemoryLoader` 和 `SkillsLoader` 通过构造函数注入，便于测试和替换 |
| 扁平包结构 | 每个模块是项目根的一级 Python 包，导入路径短 (`from tools.base import Tool`)，无需 `pip install` 即可 `python app.py` |
| 只读 Memory | 当前只加载 MEMORY.md 注入 prompt，不提供写入工具。保持极简，写入留给后续迭代 |
