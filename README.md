# iflow-bot-gateway

基于 [iflow-bot](https://github.com/iflowai/iflow-bot) v0.4.6 的 fork，修复了压缩机制和跨渠道会话问题。

> 原项目作者：**Loki** / iFlow Team（MIT License）
> Fork 维护：**李不是狼** & **妖妖酒（119）**

---

## 相对于原版的改动

### Bug 修复
- **Token 估算修正**：原版 `_estimate_session_history_tokens` 只统计 `text` 部分（约 18%），遗漏了 `functionCall`（13%）和 `functionResponse`（67%），导致压缩永远不触发。现在完整统计所有消息类型。

### 功能增强
- **跨渠道统一会话**：飞书、QQ、CLI 共享同一个 session，对话上下文互通（`_get_session_key` → `unified:default`）
- **统一并发锁**：配合统一会话，防止多渠道同时写入冲突
- **激活 CLI 内置压缩**：向 iflow CLI 传递 `compression_token_threshold=0.4` 和 `light_compression_token_threshold=0.25`，激活 CLI 的两层压缩机制（轻量去重 + LLM 摘要）

### 参数调优
- 压缩触发阈值：60000 → 80000 tokens（适配 200K 上下文窗口）
- 压缩预算：2200 → 4000 tokens（给 LLM 更多摘要空间）

### 搭配使用

建议搭配 [iflow-memory](https://github.com/plhys/iflow-memory) 记忆库一起使用，实现跨会话的长期记忆管理。

---

## 这是什么？

**iflow-bot-gateway** 是一个多渠道 AI 助手网关，基于 [iflow CLI](https://cli.iflow.cn/) 构建。它把 iflow CLI 强大的 AI Agent 能力接入到各种聊天平台，让你可以在飞书、QQ、Telegram、Discord、Slack、钉钉、WhatsApp、邮件等渠道上直接和 AI 助手对话。

**架构简述**：

```
用户消息（飞书/QQ/Telegram/...）
        ↓
  iflow-bot-gateway（本项目）
        ↓ ACP 协议（JSON-RPC over stdio）
    iflow CLI（AI Agent 引擎）
        ↓
    LLM API（Claude/GLM/Kimi/MiniMax/...）
```

Gateway 负责接收各渠道消息、管理会话、控制压缩，然后通过 ACP 协议调用 iflow CLI 完成实际的 AI 对话。

## 功能特性

- **多渠道支持** — Telegram、Discord、Slack、飞书、钉钉、QQ、WhatsApp、邮件、Mochat
- **AI 驱动** — 基于 iflow CLI，支持多种模型（Claude、GLM-5、Kimi K2.5、MiniMax M2.5 等）
- **会话管理** — 自动多用户会话管理，支持对话上下文
- **独立工作空间** — 每个 Bot 实例有独立的工作空间和记忆系统
- **访问控制** — 支持白名单、@触发等策略
- **流式输出** — Telegram 和钉钉 AI 卡片支持实时流式输出（打字机效果）
- **Stdio 模式** — 通过 stdin/stdout 直接与 iflow 通信，响应更快
- **定时任务** — 支持 cron 表达式、间隔触发、一次性定时消息
- **Ralph 工作流** — 支持 PRD 驱动的长任务编排

## 前置条件

### 1. 安装 iflow CLI

```bash
# 需要 Node.js 22+
npm i -g @iflow-ai/iflow-cli@latest
```

### 2. 登录 iflow

```bash
iflow
```

运行后选择 "Login with iFlow"，按提示完成登录授权。

## 安装

**从 GitHub 安装（推荐）：**

```bash
pip install git+https://github.com/plhys/iflow-bot-gateway.git
```

**从源码安装：**

```bash
git clone https://github.com/plhys/iflow-bot-gateway.git
cd iflow-bot-gateway
pip install -e .
```

安装后可直接使用：

```bash
iflow-bot --help
iflow-bot onboard        # 初始化配置
iflow-bot gateway start  # 启动服务
```

## 快速开始

```bash
# 1. 初始化配置文件
iflow-bot onboard

# 2. 编辑配置，启用需要的渠道
iflow-bot config -e

# 3. 启动服务
iflow-bot gateway start    # 后台运行
iflow-bot gateway run      # 前台运行（调试用）

# 4. 查看状态
iflow-bot status

# 5. 停止服务
iflow-bot gateway stop
```

## 配置

配置文件位于 `~/.iflow-bot/config.json`

### Driver 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | string | `"stdio"` | 通信模式：`stdio`（推荐）、`acp`（WebSocket）、`cli`（子进程） |
| `iflow_path` | string | `"iflow"` | iflow CLI 路径 |
| `model` | string | `"minimax-m2.5"` | 默认模型 |
| `yolo` | bool | `true` | 自动确认模式 |
| `thinking` | bool | `false` | 显示 AI 思考过程 |
| `max_turns` | int | `40` | 每个会话最大对话轮数 |
| `timeout` | int | `600` | 超时时间（秒） |
| `workspace` | string | `~/.iflow-bot/workspace` | 工作空间路径 |

### 渠道配置示例

**飞书：**

```json
{
  "feishu": {
    "enabled": true,
    "app_id": "cli_xxx",
    "app_secret": "xxx",
    "encrypt_key": "",
    "verification_token": "",
    "allow_from": []
  }
}
```

在[飞书开放平台](https://open.feishu.cn/)创建企业自建应用，启用机器人能力，配置事件订阅（使用 WebSocket，无需公网 IP）。

**QQ：**

```json
{
  "qq": {
    "enabled": true,
    "app_id": "xxx",
    "secret": "xxx",
    "allow_from": []
  }
}
```

在 [QQ 开放平台](https://q.qq.com/)创建机器人获取 App ID 和 Secret。

**Telegram：**

```json
{
  "telegram": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN",
    "allow_from": []
  }
}
```

**钉钉：**

```json
{
  "dingtalk": {
    "enabled": true,
    "client_id": "xxx",
    "client_secret": "xxx",
    "robot_code": "xxx",
    "card_template_id": "xxx",
    "card_template_key": "content",
    "allow_from": []
  }
}
```

其他渠道（Discord、Slack、WhatsApp、Email、Mochat）配置方式类似，详见原项目文档。

## CLI 命令

```bash
# 基础命令
iflow-bot version              # 版本
iflow-bot status               # 状态
iflow-bot onboard              # 初始化配置

# 服务管理
iflow-bot gateway start        # 后台启动
iflow-bot gateway run          # 前台运行
iflow-bot gateway stop         # 停止
iflow-bot gateway restart      # 重启

# 配置管理
iflow-bot config --show        # 查看配置
iflow-bot config -e            # 编辑配置
iflow-bot model glm-5          # 切换模型

# 会话管理
iflow-bot sessions             # 列出会话
iflow-bot sessions --clear     # 清除会话映射

# 定时任务
iflow-bot cron list            # 列出任务
iflow-bot cron add -n "提醒" -m "喝水了" -e 300 -d --channel feishu --to "chat_id"
iflow-bot cron remove <id>     # 删除任务

# Web 控制台
iflow-bot console --port 8787
```

### 聊天内斜杠命令

在聊天应用内发送：

| 命令 | 说明 |
|------|------|
| `/status` | 查看当前状态（模型、token 用量、压缩次数等） |
| `/new` | 开始新对话，清除上下文 |
| `/compact` | 手动压缩当前会话 |
| `/help` | 帮助信息 |
| `/model set <name>` | 切换模型 |
| `/language <en-US\|zh-CN>` | 切换语言 |
| `/skills find/add/list/remove` | 技能管理 |
| `/cron list/add/delete` | 定时任务管理 |
| `/ralph "<prompt>"` | 启动 Ralph 工作流 |

## 目录结构

```
~/.iflow-bot/
├── config.json                    # 配置文件
├── gateway.log                    # 网关日志
├── gateway.pid                    # PID 文件
├── session_mappings.json          # 会话映射
├── data/
│   ├── cron/jobs.json             # 定时任务
│   ├── media/                     # 媒体缓存
│   └── sessions/                  # 会话元数据
└── workspace/
    ├── .iflow/settings.json       # 工作空间设置
    ├── AGENTS.md                  # Agent 指令
    ├── SOUL.md                    # 人格设定
    ├── IDENTITY.md                # 身份设定
    ├── USER.md                    # 用户信息
    ├── memory/MEMORY.md           # 长期记忆
    ├── skills/                    # 已安装技能
    └── ralph/                     # Ralph 工作流数据
```

## Docker 部署

```bash
docker build -t iflow-bot:latest .
mkdir -p ./config
cp config/config.example.json ./config/config.json
# 编辑 config.json 配置渠道密钥
docker compose up -d
```

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 致谢

- [iflow CLI](https://cli.iflow.cn/) — AI Agent CLI 引擎
- [iflow-bot](https://github.com/iflowai/iflow-bot) — 原项目，作者 Loki / iFlow Team
- [iflow-memory](https://github.com/plhys/iflow-memory) — 跨会话记忆管理