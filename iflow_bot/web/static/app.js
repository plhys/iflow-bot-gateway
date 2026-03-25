const I18N_DICT = {
  "zh-CN": {
    "nav.dashboard": "仪表盘",
    "nav.chat": "Web 对话",
    "nav.conversations": "全渠道对话",
    "nav.config": "配置中心",
    "nav.logs": "实时日志",
    "common.on": "开启",
    "common.off": "关闭",
    "common.send": "发送",
    "common.filter": "筛选",
    "common.refresh": "刷新",
    "common.close": "关闭",
    "common.save": "保存",
    "common.view": "查看",
    "common.channel": "渠道",
    "common.sessions": "会话数",
    "common.messages": "消息数",
    "chat.title": "Web 对话 · 实时控制台",
    "chat.session_list": "会话列表",
    "chat.sessions": "会话",
    "chat.session_history": "会话历史",
    "chat.session_history_hint": "点击直接接管会话",
    "chat.more_actions": "更多操作",
    "chat.pinned": "置顶",
    "chat.pin": "置顶",
    "chat.unpin": "取消置顶",
    "chat.delete": "删除",
    "chat.model": "模型",
    "chat.model_context": "模型上下文",
    "chat.custom_model_id": "自定义模型 ID",
    "chat.custom_model_placeholder": "例如: minimax-m2.5",
    "chat.runtime_mode": "运行模式",
    "chat.think_mode": "思考模式",
    "chat.input_placeholder": "输入消息，Enter 发送 / Shift+Enter 换行",
    "chat.new_chat": "新对话",
    "chat.ready": "就绪",
    "chat.runtime_panel": "运行态面板",
    "chat.runtime_state": "运行态",
    "chat.elapsed": "耗时",
    "chat.text_chunks": "文本块",
    "chat.tool_calls": "工具调用",
    "chat.thought_chunks": "思考块",
    "chat.total_tokens": "总 Tokens",
    "chat.phases": "阶段",
    "chat.events": "事件",
    "phase.preparing": "准备中",
    "phase.runtime_config": "应用运行参数",
    "phase.waiting_first_chunk": "等待首包",
    "phase.streaming": "流式输出",
    "phase.finalizing": "收尾持久化",
    "phase.failed": "异常终止",
    "conv.title": "全渠道对话",
    "conv.all_channels": "全部渠道",
    "conv.search_placeholder": "搜索 chat_id 或最后消息...",
    "conv.last_time": "最后时间",
    "conv.last_message": "最后消息",
    "conv.detail_title": "对话详情",
    "conv.back_to_list": "返回会话列表",
    "dashboard.gateway_status": "Gateway 状态",
    "dashboard.gateway_running": "运行中",
    "dashboard.gateway_stopped": "已停止",
    "dashboard.total_sessions": "会话总数",
    "dashboard.cover_all_channels": "覆盖所有渠道",
    "dashboard.total_messages": "消息总量",
    "dashboard.aggregated_by_recorder": "按 recorder 数据聚合",
    "dashboard.channel_overview": "渠道概览",
    "dashboard.recent_errors": "最近错误",
    "config.enabled_channels": "启用渠道",
    "config.total_configurable_prefix": "共",
    "config.total_configurable_suffix": "个可配置渠道",
    "config.timeout": "超时",
    "config.title": "配置中心",
    "config.subtitle": "左侧渠道列表，右侧弹窗编辑字段配置。",
    "config.file": "配置文件",
    "config.edit_channel": "编辑配置",
    "config.advanced_json": "高级：全量 JSON 编辑",
    "config.json_editor": "JSON 编辑器",
    "config.validate_hint": "建议：先“校验配置”再保存",
    "config.validate": "校验配置",
    "config.save_config": "保存配置",
    "config.channel_modal_title": "渠道配置",
    "logs.title": "实时日志",
    "logs.source_gateway": "Gateway 日志",
    "logs.source_web": "Web 控制台日志",
    "logs.source_all": "全部日志",
    "logs.keyword_placeholder": "筛选关键字...",
    "logs.auto_follow": "自动跟随",
    "logs.current_source": "当前来源",
    "logs.source_hint": "支持 Web 与 Gateway 双日志源",
    "nav.mcp": "MCP 代理",
    "mcp.status_title": "MCP 代理状态",
    "mcp.running_status": "运行状态:",
    "mcp.pid": "PID:",
    "mcp.config_file": "配置文件:",
    "mcp.refresh": "刷新状态",
    "mcp.restart": "重启 MCP 代理",
    "mcp.sync": "从 iflow 同步",
    "mcp.health_check": "健康检查",
    "mcp.health_healthy": "健康",
    "mcp.health_error": "错误",
    "mcp.health_unknown": "未知",
    "mcp.servers": "MCP 服务器配置",
    "mcp.server_name": "名称",
    "mcp.server_type": "类型",
    "mcp.server_command": "命令",
    "mcp.server_status": "状态",
    "mcp.disabled": "已禁用",
    "mcp.enabled": "已启用",
    "mcp.no_servers": "未配置 MCP 服务器",
    "mcp.discovered_servers": "发现的服务",
    "mcp.discover_loading": "正在加载...",
    "mcp.health_error_message": "无法连接到 MCP 代理",
  },
  "en-US": {
    "nav.dashboard": "Dashboard",
    "nav.chat": "Web Chat",
    "nav.conversations": "Conversations",
    "nav.config": "Config",
    "nav.logs": "Live Logs",
    "common.on": "On",
    "common.off": "Off",
    "common.send": "Send",
    "common.filter": "Filter",
    "common.refresh": "Refresh",
    "common.close": "Close",
    "common.save": "Save",
    "common.view": "View",
    "common.channel": "Channel",
    "common.sessions": "Sessions",
    "common.messages": "Messages",
    "chat.title": "Web Chat · Realtime Console",
    "chat.session_list": "Session list",
    "chat.sessions": "Sessions",
    "chat.session_history": "Session history",
    "chat.session_history_hint": "Click to take over the session",
    "chat.more_actions": "More actions",
    "chat.pinned": "Pinned",
    "chat.pin": "Pin",
    "chat.unpin": "Unpin",
    "chat.delete": "Delete",
    "chat.model": "Model",
    "chat.model_context": "Model context",
    "chat.custom_model_id": "Custom model ID",
    "chat.custom_model_placeholder": "e.g. minimax-m2.5",
    "chat.runtime_mode": "Runtime mode",
    "chat.think_mode": "Think mode",
    "chat.input_placeholder": "Type a message, Enter to send / Shift+Enter for newline",
    "chat.new_chat": "New Chat",
    "chat.ready": "Ready",
    "chat.runtime_panel": "Runtime panel",
    "chat.runtime_state": "Runtime",
    "chat.elapsed": "Elapsed",
    "chat.text_chunks": "Text Chunks",
    "chat.tool_calls": "Tool Calls",
    "chat.thought_chunks": "Thought Chunks",
    "chat.total_tokens": "Total Tokens",
    "chat.phases": "Phases",
    "chat.events": "Events",
    "phase.preparing": "Preparing",
    "phase.runtime_config": "Applying runtime config",
    "phase.waiting_first_chunk": "Waiting first chunk",
    "phase.streaming": "Streaming",
    "phase.finalizing": "Finalizing",
    "phase.failed": "Failed",
    "conv.title": "Conversations",
    "conv.all_channels": "All channels",
    "conv.search_placeholder": "Search chat_id or last message...",
    "conv.last_time": "Last time",
    "conv.last_message": "Last message",
    "conv.detail_title": "Conversation Detail",
    "conv.back_to_list": "Back to list",
    "dashboard.gateway_status": "Gateway Status",
    "dashboard.gateway_running": "Running",
    "dashboard.gateway_stopped": "Stopped",
    "dashboard.total_sessions": "Total Sessions",
    "dashboard.cover_all_channels": "Across all channels",
    "dashboard.total_messages": "Total Messages",
    "dashboard.aggregated_by_recorder": "Aggregated from recorder data",
    "dashboard.channel_overview": "Channel Overview",
    "dashboard.recent_errors": "Recent Errors",
    "config.enabled_channels": "Enabled Channels",
    "config.total_configurable_prefix": "Total",
    "config.total_configurable_suffix": "configurable channels",
    "config.timeout": "Timeout",
    "config.title": "Config Center",
    "config.subtitle": "Channel list on the left, field editor in modal on the right.",
    "config.file": "Config file",
    "config.edit_channel": "Edit Config",
    "config.advanced_json": "Advanced: Full JSON Editor",
    "config.json_editor": "JSON Editor",
    "config.validate_hint": "Tip: Validate config before saving",
    "config.validate": "Validate Config",
    "config.save_config": "Save Config",
    "config.channel_modal_title": "Channel Config",
    "logs.title": "Live Logs",
    "logs.source_gateway": "Gateway Logs",
    "logs.source_web": "Web Console Logs",
    "logs.source_all": "All Logs",
    "logs.keyword_placeholder": "Filter keyword...",
    "logs.auto_follow": "Auto follow",
    "logs.current_source": "Current source",
    "logs.source_hint": "Supports both Web and Gateway logs",
    "nav.mcp": "MCP Proxy",
    "mcp.status_title": "MCP Proxy Status",
    "mcp.running_status": "Status:",
    "mcp.pid": "PID:",
    "mcp.config_file": "Config File:",
    "mcp.refresh": "Refresh",
    "mcp.restart": "Restart MCP Proxy",
    "mcp.sync": "Sync from iflow",
    "mcp.health_check": "Health Check",
    "mcp.health_healthy": "Healthy",
    "mcp.health_error": "Error",
    "mcp.health_unknown": "Unknown",
    "mcp.servers": "MCP Servers",
    "mcp.server_name": "Name",
    "mcp.server_type": "Type",
    "mcp.server_command": "Command",
    "mcp.server_status": "Status",
    "mcp.disabled": "Disabled",
    "mcp.enabled": "Enabled",
    "mcp.no_servers": "No MCP servers configured",
    "mcp.discovered_servers": "Discovered Servers",
    "mcp.discover_loading": "Loading...",
    "mcp.health_error_message": "Cannot connect to MCP Proxy",
  },
};

function _normalizeLang(lang) {
  return (lang || "").toLowerCase().startsWith("zh") ? "zh-CN" : "en-US";
}

let _lang = _normalizeLang(window.localStorage?.getItem("iflow_console_lang") || navigator.language || "zh-CN");

function t(key) {
  return I18N_DICT[_lang]?.[key] || I18N_DICT["zh-CN"]?.[key] || key;
}

function _applyI18n() {
  document.documentElement.lang = _lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n || "";
    if (key) node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.dataset.i18nPlaceholder || "";
    if (key) node.setAttribute("placeholder", t(key));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((node) => {
    const key = node.dataset.i18nTitle || "";
    if (key) node.setAttribute("title", t(key));
  });
}

async function validateConfig(token) {
  const content = document.getElementById("config-editor")?.value || "";
  const resultEl = document.getElementById("validate-result");
  if (!resultEl) return;
  const form = new FormData();
  form.set("content", content);
  const url = token ? `/api/config/validate?token=${encodeURIComponent(token)}` : "/api/config/validate";

  resultEl.textContent = _lang === "en-US" ? "Validating..." : "校验中...";
  try {
    const resp = await fetch(url, { method: "POST", body: form });
    const data = await resp.json();
    resultEl.textContent = data.message || (_lang === "en-US" ? "Validation complete" : "校验完成");
    resultEl.style.color = data.ok ? "#31d0aa" : "#ff5d7f";
  } catch (e) {
    resultEl.textContent = _lang === "en-US" ? `Validation failed: ${e}` : `校验失败: ${e}`;
    resultEl.style.color = "#ff5d7f";
  }
}

function openChannelConfigModal(channelName, enabledFlag = "0") {
  const shell = document.getElementById("channel-config-modal");
  const title = document.getElementById("channel-config-modal-title");
  const meta = document.getElementById("channel-config-modal-meta");
  const body = document.getElementById("channel-config-modal-body");
  const template = document.getElementById(`channel-config-template-${channelName}`);
  if (!shell || !title || !meta || !body || !template) return;

  title.textContent = _lang === "en-US" ? `${channelName.toUpperCase()} Config` : `${channelName.toUpperCase()} 配置`;
  meta.textContent = enabledFlag === "1"
    ? (_lang === "en-US" ? "Status: Online" : "当前状态：在线")
    : (_lang === "en-US" ? "Status: Disabled" : "当前状态：关闭");
  body.innerHTML = "";
  body.appendChild(template.content.cloneNode(true));
  _applyI18n();
  shell.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeChannelConfigModal(event) {
  if (event && event.target && event.currentTarget && event.target !== event.currentTarget) return;
  const shell = document.getElementById("channel-config-modal");
  const body = document.getElementById("channel-config-modal-body");
  if (body) body.innerHTML = "";
  if (shell) shell.classList.add("hidden");
  document.body.classList.remove("modal-open");
}

function selectChatTarget(button, token) {
  if (!button) return;
  closeHistoryMenus();
  document.querySelectorAll(".history-item.active").forEach((n) => n.classList.remove("active"));
  button.classList.add("active");
  loadChatHistory(token);
}

function closeHistoryMenus() {
  document.querySelectorAll(".history-menu").forEach((menu) => menu.classList.add("hidden"));
}

function toggleHistoryMenu(button, event) {
  if (event) event.stopPropagation();
  const root = button?.closest(".history-item");
  if (!root) return;
  const menu = root.querySelector(".history-menu");
  if (!menu) return;
  const opening = menu.classList.contains("hidden");
  closeHistoryMenus();
  if (opening) {
    const list = document.getElementById("chat-history-list");
    const listRect = list?.getBoundingClientRect();
    menu.classList.remove("open-up");
    menu.classList.remove("hidden");
    const menuRect = menu.getBoundingClientRect();
    if (listRect && menuRect.bottom > (listRect.bottom - 4)) {
      menu.classList.add("open-up");
    }
  }
}

function _findHistoryItem(channel, chatId) {
  return document.querySelector(
    `.history-item[data-channel="${CSS.escape(channel)}"][data-chat-id="${CSS.escape(chatId)}"]`,
  );
}

async function setTargetPinned(channel, chatId, pinned, token, event) {
  if (event) event.stopPropagation();
  const form = new FormData();
  form.set("channel", channel);
  form.set("chat_id", chatId);
  form.set("pinned", pinned ? "1" : "0");
  const url = token ? `/api/chat/target/pin?token=${encodeURIComponent(token)}` : "/api/chat/target/pin";
  try {
    const resp = await fetch(url, { method: "POST", body: form });
    const data = await resp.json();
    if (!data.ok) {
      _setStatus(data.message || (_lang === "en-US" ? "Pin failed" : "置顶失败"), "#ff5d7f");
      return;
    }
    window.location.reload();
  } catch (e) {
    _setStatus(_lang === "en-US" ? `Pin failed: ${e}` : `置顶失败: ${e}`, "#ff5d7f");
  }
}

async function deleteTargetHistory(channel, chatId, token, event) {
  if (event) event.stopPropagation();
  if (!window.confirm(_lang === "en-US" ? `Delete session ${channel}:${chatId}?` : `确认删除会话 ${channel}:${chatId} 吗？`)) return;
  const form = new FormData();
  form.set("channel", channel);
  form.set("chat_id", chatId);
  const url = token ? `/api/chat/target/delete?token=${encodeURIComponent(token)}` : "/api/chat/target/delete";
  try {
    const resp = await fetch(url, { method: "POST", body: form });
    const data = await resp.json();
    if (!data.ok) {
      _setStatus(data.message || (_lang === "en-US" ? "Delete failed" : "删除失败"), "#ff5d7f");
      return;
    }
    const item = _findHistoryItem(channel, chatId);
    const wasActive = Boolean(item?.classList.contains("active"));
    item?.remove();
    closeHistoryMenus();
    if (wasActive) {
      const first = document.querySelector("#chat-history-list .history-item");
      if (first) {
        first.classList.add("active");
        const pageToken = document.getElementById("chat-board")?.dataset.token || "";
        loadChatHistory(pageToken);
      } else {
        const board = document.getElementById("chat-board");
        if (board) board.innerHTML = "";
        _setStatus(_lang === "en-US" ? "Session deleted" : "会话已删除", "#31d0aa");
      }
    } else {
      _setStatus(_lang === "en-US" ? "Session deleted" : "会话已删除", "#31d0aa");
    }
  } catch (e) {
    _setStatus(_lang === "en-US" ? `Delete failed: ${e}` : `删除失败: ${e}`, "#ff5d7f");
  }
}

function toggleFold(elementId) {
  const node = document.getElementById(elementId);
  if (!node) return;
  node.classList.toggle("collapsed");
  _refreshChatShellLayout();
}

function _refreshChatShellLayout() {
  const shell = document.querySelector(".chat-shell");
  if (!shell) return;
  if (window.matchMedia("(max-width: 960px)").matches) {
    shell.style.gridTemplateColumns = "1fr";
    return;
  }
  const leftCollapsed = document.getElementById("chat-history-side")?.classList.contains("collapsed");
  const rightCollapsed = document.getElementById("chat-runtime-side")?.classList.contains("collapsed");
  const leftWidth = leftCollapsed ? 0 : 260;
  const rightWidth = rightCollapsed ? 0 : 260;
  shell.style.gridTemplateColumns = `${leftWidth}px minmax(0, 1fr) ${rightWidth}px`;
}

function _resolveChatTarget() {
  const sessionId = document.getElementById("chat-session-id")?.value || "";
  const active = document.querySelector(".history-item.active");
  const channel = (active?.dataset.channel || "web").trim() || "web";
  const chatIdInput = (active?.dataset.chatId || "").trim();
  return {
    channel,
    chatId: chatIdInput || sessionId,
    sessionId,
  };
}

function _renderMessagesToBoard(messages) {
  const board = document.getElementById("chat-board");
  if (!board) return;
  board.innerHTML = "";
  (messages || []).forEach((msg) => {
    const role = msg?.role === "user" ? "user" : "assistant";
    _appendChatBubble(role, (msg?.content || "").toString());
  });
  _scrollChatToBottom();
}

async function loadChatHistory(token) {
  const target = _resolveChatTarget();
  const board = document.getElementById("chat-board");
  if (!board) return;
  const query = new URLSearchParams({
    channel: target.channel,
    chat_id: target.chatId,
    session_id: target.sessionId,
  });
  if (token) query.set("token", token);
  try {
    const resp = await fetch(`/api/chat/history?${query.toString()}`);
    const data = await resp.json();
    if (!data.ok) {
      _setStatus(_lang === "en-US" ? "Failed to load history" : "历史加载失败", "#ff5d7f");
      return;
    }
    _renderMessagesToBoard(data.messages || []);
    _setStatus(
      _lang === "en-US" ? `History loaded: ${data.channel}:${data.chat_id}` : `已加载历史：${data.channel}:${data.chat_id}`,
      "#31d0aa",
    );
  } catch (e) {
    _setStatus(_lang === "en-US" ? `Failed to load history: ${e}` : `历史加载失败: ${e}`, "#ff5d7f");
  }
}

const webChatState = {
  currentAssistantContentNode: null,
  currentAssistantRaw: "",
  currentTurn: null,
  toolCallState: new Map(),
  turnToolIds: new Set(),
  streamStartAt: 0,
  timerId: null,
  inFlight: false,
  chunkCount: 0,
  thoughtCount: 0,
  modelContexts: {},
  lastUnsupportedSignature: "",
};

function _scrollChatToBottom() {
  const board = document.getElementById("chat-board");
  if (!board) return;
  board.scrollTop = board.scrollHeight;
  requestAnimationFrame(() => {
    board.scrollTop = board.scrollHeight;
  });
}

function _runtimeLabel(capability) {
  const map = {
    "session/set_mode": _lang === "en-US" ? "Runtime mode switch" : "运行模式动态切换",
    "session/set_model": _lang === "en-US" ? "Model switch" : "模型动态切换",
    "session/set_think": _lang === "en-US" ? "Think mode switch" : "思考开关动态切换",
    "model_runtime_config": _lang === "en-US" ? "Runtime model config" : "运行时模型配置",
  };
  return map[capability] || capability;
}

function _escapeHtml(text) {
  return (text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function _renderInlineMarkdown(text) {
  let value = _escapeHtml(text || "");
  value = value.replace(/`([^`]+)`/g, "<code>$1</code>");
  value = value.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  value = value.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  value = value.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  return value;
}

function _renderMarkdown(text) {
  const source = (text || "").replace(/\r\n/g, "\n");
  const codeBlocks = [];
  const withPlaceholders = source.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<pre><code class="lang-${_escapeHtml(lang || "plain")}">${_escapeHtml(code)}</code></pre>`);
    return `@@CODE_BLOCK_${idx}@@`;
  });

  const lines = withPlaceholders.split("\n");
  const out = [];
  let inUl = false;
  let inOl = false;

  const closeLists = () => {
    if (inUl) {
      out.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      out.push("</ol>");
      inOl = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    const trimmed = line.trim();
    if (!trimmed) {
      closeLists();
      continue;
    }
    const codeMatch = trimmed.match(/^@@CODE_BLOCK_(\d+)@@$/);
    if (codeMatch) {
      closeLists();
      out.push(codeBlocks[Number(codeMatch[1])] || "");
      continue;
    }
    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      closeLists();
      const level = heading[1].length;
      out.push(`<h${level}>${_renderInlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }
    const ul = trimmed.match(/^[-*]\s+(.+)$/);
    if (ul) {
      if (inOl) {
        out.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        out.push("<ul>");
        inUl = true;
      }
      out.push(`<li>${_renderInlineMarkdown(ul[1])}</li>`);
      continue;
    }
    const ol = trimmed.match(/^\d+\.\s+(.+)$/);
    if (ol) {
      if (inUl) {
        out.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        out.push("<ol>");
        inOl = true;
      }
      out.push(`<li>${_renderInlineMarkdown(ol[1])}</li>`);
      continue;
    }
    if (trimmed.startsWith(">")) {
      closeLists();
      out.push(`<blockquote>${_renderInlineMarkdown(trimmed.replace(/^>\s?/, ""))}</blockquote>`);
      continue;
    }
    if (/^---+$/.test(trimmed)) {
      closeLists();
      out.push("<hr>");
      continue;
    }
    closeLists();
    out.push(`<p>${_renderInlineMarkdown(trimmed)}</p>`);
  }
  closeLists();
  return out.join("");
}

function _renderMarkdownNode(node, text) {
  if (!node) return;
  node.innerHTML = _renderMarkdown(text || "");
}

function _setStatus(text, color = "#a7b4d6") {
  const status = document.getElementById("chat-status");
  if (!status) return;
  status.textContent = text;
  status.style.color = color;
}

function _setRuntimeTag(text) {
  const tag = document.getElementById("runtime-live-tag");
  if (!tag) return;
  tag.textContent = text;
}

function _updateMetric(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = `${value}`;
}

function _resetTurnArtifacts() {
  webChatState.currentTurn = null;
  webChatState.turnToolIds = new Set();
  _updateMetric("metric-tokens", "-");
}

function _startElapsed() {
  _stopElapsed();
  webChatState.streamStartAt = Date.now();
  webChatState.timerId = window.setInterval(() => {
    const elapsed = (Date.now() - webChatState.streamStartAt) / 1000;
    _updateMetric("metric-elapsed", `${elapsed.toFixed(1)}s`);
  }, 100);
}

function _stopElapsed() {
  if (webChatState.timerId !== null) {
    window.clearInterval(webChatState.timerId);
    webChatState.timerId = null;
  }
}

function _appendChatBubble(role, content) {
  const board = document.getElementById("chat-board");
  if (!board) return;
  const div = document.createElement("div");
  div.className = `bubble ${role === "user" ? "user" : "assistant"}`;
  div.innerHTML = `<div class="meta">${role}</div><div class="md-content"></div>`;
  _renderMarkdownNode(div.querySelector(".md-content"), (content ?? "").toString());
  board.appendChild(div);
  _scrollChatToBottom();
}

function _startAssistantBubble(modelLabel, modeLabel, thinkEnabled) {
  const board = document.getElementById("chat-board");
  if (!board) return null;
  const div = document.createElement("div");
  div.className = "bubble assistant";
  div.innerHTML = `
    <div class="meta">${_lang === "en-US" ? "assistant" : "assistant"} · ${modelLabel} · ${modeLabel} · think:${thinkEnabled ? "on" : "off"}</div>
    <div class="md-content"></div>
    <div class="bubble-stream-sections">
      <section class="bubble-section bubble-plan hidden">
        <h5>${_lang === "en-US" ? "Todo / Plan" : "Todo / Plan"}</h5>
        <div class="plan-list"></div>
      </section>
      <section class="bubble-section bubble-tools hidden">
        <h5>${_lang === "en-US" ? "Tool Calls" : "工具调用"}</h5>
        <div class="tools-panel-inline"></div>
      </section>
      <section class="bubble-section bubble-files hidden">
        <h5>${_lang === "en-US" ? "File References" : "文件引用"}</h5>
        <div class="file-ref-list"></div>
      </section>
    </div>`;
  board.appendChild(div);
  _scrollChatToBottom();

  webChatState.currentAssistantRaw = "";
  webChatState.currentAssistantContentNode = div.querySelector(".md-content");
  webChatState.currentTurn = {
    planSection: div.querySelector(".bubble-plan"),
    planList: div.querySelector(".bubble-plan .plan-list"),
    toolSection: div.querySelector(".bubble-tools"),
    toolsPanel: div.querySelector(".bubble-tools .tools-panel-inline"),
    fileSection: div.querySelector(".bubble-files"),
    fileList: div.querySelector(".bubble-files .file-ref-list"),
    fileRefs: new Set(),
  };
  return webChatState.currentAssistantContentNode;
}

function _appendAssistantChunk(text) {
  if (!webChatState.currentAssistantContentNode) {
    _startAssistantBubble("stream", "runtime", false);
  }
  if (webChatState.currentAssistantContentNode) {
    webChatState.currentAssistantRaw += text || "";
    _renderMarkdownNode(webChatState.currentAssistantContentNode, webChatState.currentAssistantRaw);
    _scrollChatToBottom();
  }
}

function _appendEventLine(type, text) {
  const panel = document.getElementById("chat-events");
  if (!panel) return;
  const item = document.createElement("div");
  item.className = `event-line ${type}`;
  const now = new Date();
  const ts = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
  item.textContent = `${ts}  [${type}] ${text}`;
  panel.prepend(item);
}

function _setPhase(phase, status) {
  const root = document.getElementById("chat-phases");
  if (!root) return;
  const item = root.querySelector(`[data-phase="${phase}"]`);
  if (!item) return;
  item.classList.remove("pending", "in_progress", "completed", "failed");
  item.classList.add(status || "pending");
}

function _resetPhases() {
  const root = document.getElementById("chat-phases");
  if (!root) return;
  root.querySelectorAll(".phase-item").forEach((node) => {
    node.classList.remove("in_progress", "completed", "failed");
    node.classList.add("pending");
  });
}

function _upsertToolCard(tool) {
  const panel = webChatState.currentTurn?.toolsPanel;
  if (!panel) return;
  webChatState.currentTurn?.toolSection?.classList.remove("hidden");

  const id = (tool.tool_call_id || "").toString().trim() || `tool-${Date.now()}-${Math.random()}`;
  const prev = webChatState.toolCallState.get(id) || {};
  const appendOutput = Boolean(tool.output_append);
  const incomingOutput = (tool.output ?? "").toString();
  const merged = {
    tool_call_id: id,
    tool_name: tool.tool_name || prev.tool_name || (tool.tool_call_id ? `tool:${tool.tool_call_id}` : "tool"),
    status: tool.status || prev.status || "pending",
    args: Object.keys(tool.args || {}).length ? (tool.args || {}) : (prev.args || {}),
    output: appendOutput
      ? `${(prev.output || "").toString()}${incomingOutput}`
      : (incomingOutput || (prev.output ?? "").toString()),
  };
  webChatState.toolCallState.set(id, merged);
  webChatState.turnToolIds.add(id);

  let card = panel.querySelector(`[data-tool-id="${id}"]`);
  if (!card) {
    card = document.createElement("div");
    card.className = "tool-card";
    card.dataset.toolId = id;
    card.innerHTML = `
      <button type="button" class="tool-head">
        <strong class="tool-name"></strong>
        <span class="status-pill"></span>
      </button>
      <div class="tool-body">
        <div class="tool-args"></div>
        <div class="tool-output"></div>
      </div>`;
    panel.prepend(card);
    card.querySelector(".tool-head")?.addEventListener("click", () => {
      card.classList.toggle("expanded");
    });
  }

  card.querySelector(".tool-name").textContent = merged.tool_name;
  const pill = card.querySelector(".status-pill");
  pill.textContent = merged.status;
  pill.className = `status-pill ${merged.status}`;

  const argsNode = card.querySelector(".tool-args");
  argsNode.innerHTML = `<small>${_lang === "en-US" ? "args" : "args"}</small><pre></pre>`;
  argsNode.querySelector("pre").textContent = JSON.stringify(merged.args || {}, null, 2);
  const outputNode = card.querySelector(".tool-output");
  outputNode.innerHTML = `<small>${_lang === "en-US" ? "output" : "output"}</small><pre></pre>`;
  outputNode.querySelector("pre").textContent = merged.output || "(empty)";
}

function _renderPlanEntries(entries) {
  const node = webChatState.currentTurn?.planList;
  if (!node) return;
  if (!Array.isArray(entries) || !entries.length) return;
  webChatState.currentTurn?.planSection?.classList.remove("hidden");
  node.innerHTML = "";
  entries.forEach((entry, idx) => {
    const item = document.createElement("div");
    const status = (entry.status || "pending").toString();
    item.className = `plan-item ${status}`;
    item.innerHTML = `<span class="plan-index">${idx + 1}</span><span class="plan-content"></span><span class="plan-status">${status}</span>`;
    item.querySelector(".plan-content").textContent = (entry.content || "").toString();
    node.appendChild(item);
  });
}

function _addFileRef(ref) {
  const node = webChatState.currentTurn?.fileList;
  if (!node) return;
  const path = (ref.path || "").toString().trim();
  if (!path) return;
  webChatState.currentTurn?.fileSection?.classList.remove("hidden");
  const lineStart = ref.line_start ?? ref.lineStart;
  const marker = lineStart ? `${path}:${lineStart}` : path;
  if (webChatState.currentTurn?.fileRefs?.has(marker)) return;
  webChatState.currentTurn?.fileRefs?.add(marker);
  const row = document.createElement("div");
  row.className = "file-ref-item";
  row.textContent = marker;
  node.prepend(row);
}

function _parseSseFrames(buffer) {
  const frames = [];
  let rest = buffer;
  while (true) {
    const idx = rest.indexOf("\n\n");
    if (idx === -1) break;
    const frame = rest.slice(0, idx);
    rest = rest.slice(idx + 2);
    if (!frame.trim()) continue;
    let event = "message";
    const dataLines = [];
    frame.split("\n").forEach((line) => {
      if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trimStart());
      }
    });
    let payload = {};
    try {
      payload = JSON.parse(dataLines.join("\n") || "{}");
    } catch (_) {
      payload = {};
    }
    frames.push({ event, payload });
  }
  return { frames, rest };
}

function _handleStreamEvent(eventType, data) {
  if (eventType === "assistant_chunk") {
    webChatState.chunkCount += 1;
    _updateMetric("metric-chunks", webChatState.chunkCount);
    _appendAssistantChunk(data.text || "");
  } else if (eventType === "thought_chunk") {
    webChatState.thoughtCount += 1;
    _updateMetric("metric-thoughts", webChatState.thoughtCount);
    _appendEventLine("thought", data.text || "");
  } else if (eventType === "tool_call") {
    _appendEventLine("tool", `${data.tool_name || "tool"} · ${data.status || "pending"}`);
    _upsertToolCard(data);
    _updateMetric("metric-tools", webChatState.turnToolIds.size);
  } else if (eventType === "status") {
    _appendEventLine("status", data.message || "");
  } else if (eventType === "tool_output") {
    const toolCallId = (data.tool_call_id || "").toString().trim();
    if (toolCallId || data.tool_name) {
      _upsertToolCard({
        tool_call_id: toolCallId,
        tool_name: data.tool_name || "",
        args: data.args || {},
        status: data.status || "in_progress",
        output: data.content || "",
        output_append: true,
      });
      _updateMetric("metric-tools", webChatState.turnToolIds.size);
    } else {
      _appendEventLine("tool", data.content || "(tool update)");
    }
  } else if (eventType === "plan") {
    _renderPlanEntries(data.entries || []);
    _appendEventLine("status", _lang === "en-US" ? "Task plan updated" : "收到任务清单更新");
  } else if (eventType === "usage") {
    const total = data.total_tokens ?? "-";
    _updateMetric("metric-tokens", total);
  } else if (eventType === "file_ref") {
    _addFileRef(data || {});
  } else if (eventType === "warning") {
    _appendEventLine("warning", data.message || (_lang === "en-US" ? "warning" : "warning"));
  } else if (eventType === "approval") {
    const t = (data.update_type || "approval").toString();
    _appendEventLine("status", _lang === "en-US" ? `Approval required: ${t}` : `需要确认: ${t}`);
  } else if (eventType === "raw_event") {
    const t = (data.update_type || "event").toString();
    _appendEventLine("status", `raw: ${t}`);
  } else if (eventType === "runtime_update") {
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    const unsupported = Array.isArray(data.unsupported) ? data.unsupported : [];
    const unsupportedDetails = Array.isArray(data.unsupported_details) ? data.unsupported_details : [];
    if (warnings.length) {
      warnings.forEach((w) => _appendEventLine("warning", w));
    }
    if (unsupported.length) {
      const uniqueUnsupported = Array.from(new Set(unsupported));
      const signature = uniqueUnsupported.slice().sort().join("|");
      if (webChatState.lastUnsupportedSignature !== signature) {
        const readable = uniqueUnsupported.map(_runtimeLabel).join("、");
        _appendEventLine(
          "status",
          _lang === "en-US"
            ? `Runtime capabilities unavailable: ${readable} (ACP/stdio runtime API does not support dynamic updates, downgraded automatically)`
            : `runtime 部分能力不可用：${readable}（当前 ACP/stdio 运行时接口不支持动态设置，已自动降级）`,
        );
        const seenReason = new Set();
        unsupportedDetails.forEach((item) => {
          const label = item?.label || _runtimeLabel(item?.key || "");
          const reason = (item?.reason || "").toString().trim();
          const key = `${label}::${reason}`;
          if (label && reason && !seenReason.has(key)) {
            seenReason.add(key);
            _appendEventLine("warning", `${label}: ${reason}`);
          }
        });
        webChatState.lastUnsupportedSignature = signature;
      }
    } else {
      _appendEventLine(
        "status",
        _lang === "en-US"
          ? `Runtime applied model=${data.model_applied || "-"}`
          : `runtime已应用 model=${data.model_applied || "-"}`,
      );
    }
  } else if (eventType === "phase") {
    _setPhase(data.phase || "", data.status || "pending");
  } else if (eventType === "done") {
    if (webChatState.currentAssistantContentNode && data.content) {
      webChatState.currentAssistantRaw = data.content;
      _renderMarkdownNode(webChatState.currentAssistantContentNode, data.content);
      _scrollChatToBottom();
    }
    _setStatus(_lang === "en-US" ? "Completed" : "已完成", "#31d0aa");
    _setRuntimeTag("done");
  } else if (eventType === "error") {
    _setStatus(data.message || (_lang === "en-US" ? "Execution error" : "执行出错"), "#ff5d7f");
    _setRuntimeTag("error");
    _setPhase("failed", "failed");
    _appendEventLine("error", data.message || "unknown error");
  }
}

function _setSendBusy(busy) {
  const btn = document.getElementById("chat-send-btn");
  const input = document.getElementById("chat-input");
  webChatState.inFlight = busy;
  if (btn) btn.disabled = busy;
  if (input) input.disabled = busy;
}

function _syncModelContext() {
  const select = document.getElementById("chat-model");
  const chip = document.getElementById("chat-model-context");
  if (!select || !chip) return;
  const selected = select.value;
  const ctx = webChatState.modelContexts?.[selected];
  chip.textContent = ctx ? `${ctx.toLocaleString()} tokens` : "unknown";
}

async function sendWebChat(event, token) {
  event.preventDefault();
  if (webChatState.inFlight) return false;

  const input = document.getElementById("chat-input");
  const target = _resolveChatTarget();
  const sid = target.sessionId;
  const modelSelect = document.getElementById("chat-model");
  const modelCustom = document.getElementById("chat-model-custom");
  const runtimeMode = document.getElementById("chat-runtime-mode");
  const thinkEnabled = document.getElementById("chat-think-enabled");
  if (!input || !sid) return false;

  const message = input.value.trim();
  if (!message) return false;

  const modelLabel = modelSelect?.value || "";
  const model = (modelCustom?.value || "").trim() || modelLabel;
  const mode = runtimeMode?.value || "yolo";
  const think = (thinkEnabled?.value || "0") === "1" ? "1" : "0";
  const thinkOn = think === "1";
  const thinkText = thinkOn ? "on" : "off";

  _appendChatBubble("user", message);
  input.value = "";
  _setSendBusy(true);
  _setStatus(_lang === "en-US" ? "Streaming..." : "流式处理中...", "#a7b4d6");
  _setRuntimeTag("streaming");
  webChatState.chunkCount = 0;
  webChatState.thoughtCount = 0;
  _resetTurnArtifacts();
  _updateMetric("metric-chunks", 0);
  _updateMetric("metric-thoughts", 0);
  _updateMetric("metric-tools", 0);
  _updateMetric("metric-elapsed", "0.0s");
  _resetPhases();
  _setPhase("preparing", "in_progress");
  _startAssistantBubble(modelLabel || model, mode, thinkOn);
  _appendEventLine("status", `run channel=${target.channel} chat_id=${target.chatId} mode=${mode} think=${thinkText} model=${model}`);
  _startElapsed();

  const form = new FormData();
  form.set("message", message);
  form.set("session_id", sid);
  form.set("channel", target.channel);
  form.set("chat_id", target.chatId);
  form.set("model", model);
  form.set("runtime_mode", mode);
  form.set("think_enabled", think);
  const url = token ? `/api/chat/stream?token=${encodeURIComponent(token)}` : "/api/chat/stream";

  try {
    const resp = await fetch(url, { method: "POST", body: form });
    if (!resp.ok || !resp.body) {
      _setStatus(_lang === "en-US" ? `Request failed: HTTP ${resp.status}` : `请求失败: HTTP ${resp.status}`, "#ff5d7f");
      _setRuntimeTag("error");
      return false;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parsed = _parseSseFrames(buffer);
      buffer = parsed.rest;
      parsed.frames.forEach(({ event, payload }) => _handleStreamEvent(event, payload));
    }
  } catch (e) {
    _setStatus(_lang === "en-US" ? `Request failed: ${e}` : `请求失败: ${e}`, "#ff5d7f");
    _setRuntimeTag("error");
    _appendEventLine("error", String(e));
  } finally {
    _stopElapsed();
    _setSendBusy(false);
    webChatState.currentAssistantContentNode = null;
    webChatState.currentAssistantRaw = "";
    webChatState.currentTurn = null;
  }
  return false;
}

async function resetWebChat(token) {
  const target = _resolveChatTarget();
  const sid = target.sessionId;
  const board = document.getElementById("chat-board");
  if (!sid || !board) return;
  const form = new FormData();
  form.set("session_id", sid);
  form.set("channel", target.channel);
  form.set("chat_id", target.chatId);
  const url = token ? `/api/chat/reset?token=${encodeURIComponent(token)}` : "/api/chat/reset";
  try {
    await fetch(url, { method: "POST", body: form });
    board.innerHTML = "";
    const panel = document.getElementById("chat-events");
    if (panel) panel.innerHTML = "";
    webChatState.toolCallState.clear();
    _resetTurnArtifacts();
    _updateMetric("metric-tools", 0);
    _updateMetric("metric-chunks", 0);
    _updateMetric("metric-thoughts", 0);
    _updateMetric("metric-elapsed", "0.0s");
    _resetPhases();
    _setRuntimeTag("idle");
    _setStatus(_lang === "en-US" ? "Started a new chat" : "已开启新对话", "#31d0aa");
    webChatState.currentAssistantContentNode = null;
    webChatState.currentAssistantRaw = "";
  } catch (e) {
    _setStatus(_lang === "en-US" ? `Reset failed: ${e}` : `重置失败: ${e}`, "#ff5d7f");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const langSwitch = document.getElementById("console-lang-switch");
  if (langSwitch) {
    langSwitch.value = _lang;
    langSwitch.addEventListener("change", () => {
      _lang = _normalizeLang(langSwitch.value);
      window.localStorage?.setItem("iflow_console_lang", _lang);
      _applyI18n();
    });
  }
  _applyI18n();

  const modelContextRaw = document.getElementById("chat-model-context-data")?.textContent || "{}";
  try {
    webChatState.modelContexts = JSON.parse(modelContextRaw);
  } catch (_) {
    webChatState.modelContexts = {};
  }
  _syncModelContext();
  const modelSelect = document.getElementById("chat-model");
  if (modelSelect) {
    modelSelect.addEventListener("change", _syncModelContext);
  }

  const input = document.getElementById("chat-input");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        document.getElementById("chat-form")?.requestSubmit();
      }
    });
  }

  const historyList = document.getElementById("chat-history-list");
  const pageToken = document.getElementById("chat-board")?.dataset.token || "";
  if (historyList) {
    historyList.querySelectorAll(".history-item").forEach((node) => {
      node.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectChatTarget(node, pageToken);
        }
      });
    });
    const first = historyList.querySelector(".history-item");
    if (first) {
      first.classList.add("active");
      loadChatHistory(pageToken);
    }
  }

  const logsNode = document.getElementById("live-logs");
  if (logsNode) {
    let cursor = Number(logsNode.dataset.cursor || "0");
    const source = logsNode.dataset.source || "gateway";
    const keyword = logsNode.dataset.keyword || "";
    let autoFollow = (logsNode.dataset.auto || "0") === "1";
    const token = logsNode.dataset.token || "";
    let polling = false;
    const autoFollowInput = document.getElementById("logs-auto-follow");

    if (autoFollowInput) {
      autoFollowInput.checked = autoFollow;
      autoFollowInput.addEventListener("change", () => {
        autoFollow = Boolean(autoFollowInput.checked);
        logsNode.dataset.auto = autoFollow ? "1" : "0";
        if (autoFollow) logsNode.scrollTop = logsNode.scrollHeight;
      });
    }

    const poll = async () => {
      if (!autoFollow || polling) return;
      polling = true;
      try {
        const useIncremental = source !== "all";
        const query = new URLSearchParams({
          source,
          keyword,
          since: useIncremental ? String(cursor) : "0",
          limit: "240",
        });
        if (token) query.set("token", token);
        const resp = await fetch(`/api/logs/tail?${query.toString()}`);
        const data = await resp.json();
        if (data.ok && Array.isArray(data.lines) && data.lines.length) {
          if (useIncremental) {
            const chunk = `${data.lines.join("\n")}\n`;
            logsNode.textContent = `${logsNode.textContent}${chunk}`;
            cursor = Number(data.cursor || cursor);
          } else {
            logsNode.textContent = `${data.lines.join("\n")}\n`;
          }
          if (autoFollow) {
            logsNode.scrollTop = logsNode.scrollHeight;
          }
        }
      } catch (_) {
      } finally {
        polling = false;
      }
    };

    if (autoFollow) logsNode.scrollTop = logsNode.scrollHeight;
    window.setInterval(poll, 1200);
  }

  document.querySelectorAll(".md-content[data-render-markdown='1']").forEach((node) => {
    _renderMarkdownNode(node, node.textContent || "");
  });

  ["chat-history-side", "chat-runtime-side"].forEach((id) => {
    const node = document.getElementById(id);
    if (!node) return;
    node.classList.remove("collapsed");
  });
  _refreshChatShellLayout();
  window.addEventListener("resize", _refreshChatShellLayout);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeChannelConfigModal();
      closeHistoryMenus();
    }
  });

  document.addEventListener("click", () => {
    closeHistoryMenus();
  });
});
