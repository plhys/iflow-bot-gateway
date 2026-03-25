# iflow-bot-gateway

基于 [iflow-bot](https://github.com/iflowai/iflow-bot) v0.4.6 的 fork，修复了压缩机制和跨渠道会话问题。

> 原项目作者：**Loki** / iFlow Team（MIT License）
> Fork 维护：**李不是狼**

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

## 安装

```bash
pip install git+https://github.com/plhys/iflow-bot-gateway.git
```

## 搭配使用

建议搭配 [iflow-memory](https://github.com/plhys/iflow-memory) 记忆库一起使用，实现跨会话的长期记忆管理。

## 配置

与原版 iflow-bot 配置方式相同，参考 `~/.iflow-bot/config.json`。

## 许可证

MIT License — 详见 [LICENSE](LICENSE)
