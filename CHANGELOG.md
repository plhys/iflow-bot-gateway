# Changelog

## [0.4.0] - 2026-03-27

重大更新：飞书交互体验全面升级，新增思考状态显示、消息撤回取消、流式卡片优化。

### 新功能

- **飞书思考状态显示** — 当 iFlow CLI 进入思考阶段时，飞书卡片 header 显示"💭 不要急，容我想想"并实时计时，每 3 秒更新一次。用户不再面对无反馈的等待。
- **消息撤回 = 取消处理** — 用户在飞书撤回消息后，gateway 自动取消正在进行的处理任务（task.cancel + ACP session/cancel），节省 token 和算力。撤回后原卡片 patch 为"⌫ 已撤回，处理已取消"，不会创建多余卡片。
- **飞书 system 消息过滤** — `msg_type=system` 的消息（如"你撤回了一条消息重新编辑"）不再被当作用户消息处理。
- **ExecutionInfo 数据模型** — 新增 `ExecutionInfo` dataclass，统一传递模型名、思考/回复耗时、剩余上下文百分比等信息。
- **飞书富文本卡片** — 流式回复使用 interactive card，header 动态显示处理阶段（思考中/回复中/已完成）、模型名、耗时、剩余上下文。

### 修复

- **manager.py 日志不可见** — 从 stdlib `logging` 迁移到 `loguru`，修复频道管理器所有日志被静默丢弃的问题。
- **ACP cancel 调用链修复** — cancel 方法在 `ACPClient._client` 上而非 `ACPAdapter`，修正调用路径。
- **流式 cancel 卡片错位** — 撤回后不再创建新卡片，而是 patch 到原有 placeholder 卡片上，避免后续回复关联到错误的卡片。
- **流式 CancelledError 泄漏** — `_process_with_streaming` 现在正确处理 `asyncio.CancelledError`，确保 placeholder task 被清理、缓冲区被释放。

### 改进

- **ACP 统一会话架构** — 所有渠道共享同一个 ACP session（`unified:default`），飞书和终端客户端无缝切换。
- **wall-clock 计时** — 飞书卡片使用前端侧 wall-clock 计时，避免因网络延迟导致的计时不准。
- **中文状态文案** — 思考完成"💭 想好了"、回复中"📝 回复中"、已完成"✅ 已完成"、剩余上下文"剩余 xx%"。

### 文件变更

| 文件 | 改动 |
|------|------|
| `iflow_bot/engine/loop.py` | +406 行：思考状态推送、撤回取消、active task 跟踪、CancelledError 处理 |
| `iflow_bot/channels/feishu.py` | +372 行：撤回事件注册、system 消息过滤、富文本卡片、wall-clock 计时 |
| `iflow_bot/engine/acp.py` | +70 行：ACP cancel 支持 |
| `iflow_bot/bus/events.py` | +22 行：ExecutionInfo dataclass |
| `iflow_bot/channels/manager.py` | loguru 迁移 |
| `iflow_bot/engine/adapter.py` | chat_stream 回调支持 |
| `iflow_bot/cli/commands.py` | gateway 启动优化 |
