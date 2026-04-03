"""Feishu/Lark channel implementation using lark-oapi SDK with WebSocket long connection.

使用 lark-oapi SDK 实现飞书 Channel，通过 WebSocket 长连接接收消息。
无需公网 IP 或 webhook 配置。
"""

import asyncio
import contextlib
import json
import logging
import os
import random
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional

from iflow_bot.bus.events import OutboundMessage
from iflow_bot.bus.events import ExecutionInfo
from iflow_bot.bus.events import InboundMessage
from iflow_bot.bus.queue import MessageBus
from iflow_bot.channels.base import BaseChannel
from iflow_bot.channels.manager import register_channel
from iflow_bot.config.schema import FeishuConfig

try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import (
        CreateFileRequest,
        CreateFileRequestBody,
        CreateImageRequest,
        CreateImageRequestBody,
        DeleteMessageReactionRequest,
        CreateMessageRequest,
        CreateMessageRequestBody,
        CreateMessageReactionRequest,
        CreateMessageReactionRequestBody,
        Emoji,
        FollowUp,
        GetMessageResourceRequest,
        PatchMessageRequest,
        PatchMessageRequestBody,
        PushFollowUpMessageRequest,
        PushFollowUpMessageRequestBody,
        P2ImChatAccessEventBotP2pChatEnteredV1,
        P2ImMessageMessageReadV1,
        P2ImMessageRecalledV1,
        P2ImMessageReceiveV1,
        P2ImMessageReactionCreatedV1,
        P2ImMessageReactionDeletedV1,
    )
    from lark_oapi.api.speech_to_text.v1 import (
        FileRecognizeSpeechRequest,
        FileRecognizeSpeechRequestBody,
        FileConfig,
        Speech,
    )
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    lark = None  # type: ignore
    Emoji = None  # type: ignore


logger = logging.getLogger(__name__)


# Message type display mapping
MSG_TYPE_MAP = {
    "image": "[image]",
    "audio": "[audio]",
    "file": "[file]",
    "sticker": "[sticker]",
}


def _extract_share_card_content(content_json: dict, msg_type: str) -> str:
    """Extract text representation from share cards and interactive messages."""
    parts = []

    if msg_type == "share_chat":
        parts.append(f"[shared chat: {content_json.get('chat_id', '')}]")
    elif msg_type == "share_user":
        parts.append(f"[shared user: {content_json.get('user_id', '')}]")
    elif msg_type == "interactive":
        parts.extend(_extract_interactive_content(content_json))
    elif msg_type == "share_calendar_event":
        parts.append(f"[shared calendar event: {content_json.get('event_key', '')}]")
    elif msg_type == "system":
        parts.append("[system message]")
    elif msg_type == "merge_forward":
        parts.append("[merged forward messages]")

    return "\n".join(parts) if parts else f"[{msg_type}]"


def _extract_interactive_content(content: dict) -> list[str]:
    """Recursively extract text and links from interactive card content."""
    parts = []

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return [content] if content.strip() else []

    if not isinstance(content, dict):
        return parts

    if "title" in content:
        title = content["title"]
        if isinstance(title, dict):
            title_content = title.get("content", "") or title.get("text", "")
            if title_content:
                parts.append(f"title: {title_content}")
        elif isinstance(title, str):
            parts.append(f"title: {title}")

    elements = content.get("elements")
    if isinstance(elements, list):
        for element in elements:
            parts.extend(_extract_element_content(element))

    card = content.get("card", {})
    if card:
        parts.extend(_extract_interactive_content(card))

    header = content.get("header", {})
    if header:
        header_title = header.get("title", {})
        if isinstance(header_title, dict):
            header_text = header_title.get("content", "") or header_title.get("text", "")
            if header_text:
                parts.append(f"title: {header_text}")

    return parts


def _extract_element_content(element: dict) -> list[str]:
    """Extract content from a single card element."""
    parts = []

    if not isinstance(element, dict):
        return parts

    tag = element.get("tag", "")

    if tag in ("markdown", "lark_md"):
        content = element.get("content", "")
        if content:
            parts.append(content)

    elif tag == "div":
        text = element.get("text", {})
        if isinstance(text, dict):
            text_content = text.get("content", "") or text.get("text", "")
            if text_content:
                parts.append(text_content)
        elif isinstance(text, str):
            parts.append(text)
        for field in element.get("fields", []):
            if isinstance(field, dict):
                field_text = field.get("text", {})
                if isinstance(field_text, dict):
                    c = field_text.get("content", "")
                    if c:
                        parts.append(c)

    elif tag == "a":
        href = element.get("href", "")
        text = element.get("text", "")
        if href:
            parts.append(f"link: {href}")
        if text:
            parts.append(text)

    elif tag == "button":
        text = element.get("text", {})
        if isinstance(text, dict):
            c = text.get("content", "")
            if c:
                parts.append(c)
        url = element.get("url", "") or element.get("multi_url", {}).get("url", "")
        if url:
            parts.append(f"link: {url}")

    elif tag == "img":
        alt = element.get("alt", {})
        parts.append(alt.get("content", "[image]") if isinstance(alt, dict) else "[image]")

    elif tag == "note":
        for ne in element.get("elements", []):
            parts.extend(_extract_element_content(ne))

    elif tag == "column_set":
        for col in element.get("columns", []):
            for ce in col.get("elements", []):
                parts.extend(_extract_element_content(ce))

    elif tag == "plain_text":
        content = element.get("content", "")
        if content:
            parts.append(content)

    else:
        for ne in element.get("elements", []):
            parts.extend(_extract_element_content(ne))

    return parts


def _extract_post_text(content_json: dict) -> str:
    """Extract plain text from Feishu post (rich text) message content."""

    parts, _ = _extract_post_parts(content_json)
    text = "\n".join(p for p in parts if p).strip()
    return text



def _extract_post_parts(content_json: dict) -> tuple[list[str], list[dict[str, Any]]]:
    """Extract text parts and embedded resource references from Feishu post content.

    Returns:
        (text_parts, resources)
        resources item example:
          {"type": "image", "image_key": "..."}
          {"type": "file", "file_key": "..."}
          {"type": "media", "file_key": "..."}
    """

    def walk_element(element: Any, text_parts: list[str], resources: list[dict[str, Any]]) -> None:
        if not isinstance(element, dict):
            return

        tag = element.get("tag")
        if tag == "text":
            text = element.get("text", "")
            if text:
                text_parts.append(text)
        elif tag == "a":
            text = element.get("text", "")
            href = element.get("href", "")
            if text:
                text_parts.append(text)
            if href:
                text_parts.append(f"link: {href}")
        elif tag == "at":
            text_parts.append(f"@{element.get('user_name', 'user')}")
        elif tag == "img":
            image_key = element.get("image_key") or element.get("file_key")
            alt = element.get("alt", "") or "[image]"
            text_parts.append(str(alt))
            if image_key:
                resources.append({"type": "image", "image_key": image_key})
        elif tag in ("file", "media", "audio"):
            file_key = element.get("file_key")
            name = element.get("file_name") or element.get("name") or f"[{tag}]"
            text_parts.append(str(name))
            if file_key:
                resources.append({"type": tag, "file_key": file_key})
        elif tag == "emotion":
            text_parts.append(element.get("emoji_type", "[emoji]"))
        elif tag == "table":
            text_parts.append("[table]")
        else:
            # recursively walk nested containers
            for key in ("elements", "content", "columns", "fields", "children"):
                value = element.get(key)
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, list):
                            for sub in item:
                                walk_element(sub, text_parts, resources)
                        else:
                            walk_element(item, text_parts, resources)

    def extract_from_lang(lang_content: dict) -> tuple[list[str], list[dict[str, Any]]]:
        if not isinstance(lang_content, dict):
            return [], []
        title = lang_content.get("title", "")
        content_blocks = lang_content.get("content", [])
        if not isinstance(content_blocks, list):
            return [], []

        text_parts: list[str] = []
        resources: list[dict[str, Any]] = []
        if title:
            text_parts.append(title)
        for block in content_blocks:
            if not isinstance(block, list):
                continue
            for element in block:
                walk_element(element, text_parts, resources)
        return text_parts, resources

    if "content" in content_json:
        text_parts, resources = extract_from_lang(content_json)
        if text_parts or resources:
            return text_parts, resources

    for lang_key in ("zh_cn", "en_us", "ja_jp"):
        lang_content = content_json.get(lang_key)
        text_parts, resources = extract_from_lang(lang_content)
        if text_parts or resources:
            return text_parts, resources

    return [], []


@register_channel("feishu")
class FeishuChannel(BaseChannel):
    """Feishu/Lark channel using WebSocket long connection.

    Uses WebSocket to receive events - no public IP or webhook required.

    Requires:
    - App ID and App Secret from Feishu Open Platform
    - Bot capability enabled
    - Event subscription enabled (im.message.receive_v1)

    Attributes:
        name: Channel name identifier
        config: FeishuConfig configuration object
        bus: MessageBus instance
        _client: Lark client for API calls
        _ws_client: WebSocket client for long connection
        _ws_thread: Thread running WebSocket client
        _processed_message_ids: Ordered deduplication cache
        _loop: Async event loop reference
    """

    name = "feishu"
    _API_TIMEOUT = 30.0  # seconds

    def __init__(self, config: FeishuConfig, bus: MessageBus):
        """Initialize Feishu Channel.

        Args:
            config: FeishuConfig configuration object
            bus: MessageBus instance
        """
        super().__init__(config, bus)
        self.config: FeishuConfig = config
        self._client: Any = None
        self._ws_client: Any = None
        self._ws_thread: Optional[threading.Thread] = None
        self._ws_loop: Optional[asyncio.AbstractEventLoop] = None
        self._processed_message_ids: OrderedDict[str, None] = OrderedDict()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._streaming_message_ids: dict[str, str] = {}
        self._streaming_last_content: dict[str, str] = {}
        self._streaming_start_time: dict[str, float] = {}  # wall-clock: 消息创建时间
        self._typing_reaction_ids: dict[str, str] = {}
        self._typing_reaction_timestamps: dict[str, float] = {}

    async def start(self) -> None:
        """Start the Feishu bot with WebSocket long connection."""
        if not FEISHU_AVAILABLE:
            logger.error("Feishu SDK not installed. Run: pip install lark-oapi")
            return

        # 降噪：屏蔽 Lark SDK 对未注册事件（如 reaction/message_read）的错误日志刷屏
        for sdk_logger_name in ("lark_oapi", "lark_oapi.ws", "lark_oapi.ws.client"):
            sdk_logger = logging.getLogger(sdk_logger_name)
            sdk_logger.setLevel(logging.CRITICAL)
            sdk_logger.propagate = False

        if not self.config.app_id or not self.config.app_secret:
            logger.error("Feishu app_id and app_secret not configured")
            return

        self._running = True
        self._loop = asyncio.get_running_loop()

        # Create Lark client for sending messages
        self._client = lark.Client.builder() \
            .app_id(self.config.app_id) \
            .app_secret(self.config.app_secret) \
            .log_level(lark.LogLevel.ERROR) \
            .build()

        # Create event handler (register message receive and reaction events)
        event_handler = lark.EventDispatcherHandler.builder(
            self.config.encrypt_key or "",
            self.config.verification_token or "",
        ).register_p2_im_message_receive_v1(
            self._on_message_sync
        ).register_p2_im_message_reaction_created_v1(
            self._on_reaction_created_sync
        ).register_p2_im_message_reaction_deleted_v1(
            self._on_reaction_deleted_sync
        ).register_p2_im_message_recalled_v1(
            self._on_message_recalled_sync
        ).register_p2_im_message_message_read_v1(
            self._on_message_read_sync
        ).register_p2_im_chat_access_event_bot_p2p_chat_entered_v1(
            self._on_bot_p2p_chat_entered_sync
        ).build()

        # Create WebSocket client for long connection
        self._ws_client = lark.ws.Client(
            self.config.app_id,
            self.config.app_secret,
            event_handler=event_handler,
            log_level=lark.LogLevel.ERROR
        )

        # Start WebSocket client in a separate thread with reconnect loop
        def run_ws() -> None:
            reconnect_delay = 5
            max_reconnect_delay = 300  # 5 minutes cap
            while self._running:
                new_loop: Optional[asyncio.AbstractEventLoop] = None
                try:
                    # 关键修复：lark_oapi/ws/client.py 在模块级别调用 asyncio.get_event_loop()
                    # 并保存在模块变量中。我们需要替换这个变量为新线程的事件循环
                    import lark_oapi.ws.client as ws_client_module

                    # 创建新的事件循环并替换模块变量
                    new_loop = asyncio.new_event_loop()
                    self._ws_loop = new_loop
                    asyncio.set_event_loop(new_loop)
                    ws_client_module.loop = new_loop

                    # Reset delay before blocking start() — if we got here, connection setup succeeded
                    reconnect_delay = 5

                    # 现在可以安全地调用 start()
                    self._ws_client.start()
                except RuntimeError as e:
                    if not self._running and "Event loop stopped before Future completed" in str(e):
                        logger.debug("Feishu WebSocket loop stopped during shutdown")
                    else:
                        logger.warning(f"Feishu WebSocket error: {e}")
                except Exception as e:
                    logger.warning(f"Feishu WebSocket error: {e}")
                finally:
                    if new_loop is not None:
                        pending = [task for task in asyncio.all_tasks(new_loop) if not task.done()]
                        for task in pending:
                            task.cancel()
                        if pending:
                            with contextlib.suppress(Exception):
                                new_loop.run_until_complete(
                                    asyncio.gather(*pending, return_exceptions=True)
                                )
                        with contextlib.suppress(Exception):
                            new_loop.run_until_complete(new_loop.shutdown_asyncgens())
                        with contextlib.suppress(Exception):
                            new_loop.close()
                        if self._ws_loop is new_loop:
                            self._ws_loop = None
                if self._running:
                    jitter = random.uniform(0, reconnect_delay * 0.3)
                    time.sleep(reconnect_delay + jitter)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)

        self._ws_thread = threading.Thread(target=run_ws, daemon=True)
        self._ws_thread.start()

        logger.info("Feishu bot started with WebSocket long connection")
        logger.info("No public IP required - using WebSocket to receive events")

        # Keep running until stopped; periodically clean up stale state
        cleanup_counter = 0
        while self._running:
            await asyncio.sleep(1)
            cleanup_counter += 1
            if cleanup_counter >= 60:  # 每 60 秒清理一次
                cleanup_counter = 0
                try:
                    await self._cleanup_stale_reactions()
                    # 清理超过 5 分钟未更新的流式残留状态
                    now = time.time()
                    stale_streams = [
                        k for k, v in self._streaming_last_content.items()
                        if k in self._streaming_message_ids
                    ]
                    for k in stale_streams:
                        self._streaming_message_ids.pop(k, None)
                        self._streaming_last_content.pop(k, None)
                        self._streaming_start_time.pop(k, None)
                    if stale_streams:
                        logger.info(f"Cleaned {len(stale_streams)} stale streaming entries")
                except Exception as e:
                    logger.debug(f"Periodic cleanup error: {e}")

    async def stop(self) -> None:
        """Stop the Feishu bot."""
        self._running = False
        ws_loop = self._ws_loop  # snapshot to avoid race with WS thread
        if ws_loop and self._ws_client:
            def _shutdown_ws() -> None:
                async def _close() -> None:
                    with contextlib.suppress(Exception):
                        await self._ws_client._disconnect()
                    current = asyncio.current_task()
                    for task in asyncio.all_tasks():
                        if task is not current:
                            task.cancel()
                    asyncio.get_running_loop().stop()

                asyncio.create_task(_close())

            with contextlib.suppress(Exception):
                ws_loop.call_soon_threadsafe(_shutdown_ws)
        if self._ws_thread and self._ws_thread.is_alive():
            await asyncio.to_thread(self._ws_thread.join, 5)
        self._ws_thread = None
        logger.info("Feishu bot stopped")

    # Regex patterns for markdown conversion
    _TABLE_RE = re.compile(
        r"((?:^[ \t]*\|.+\|[ \t]*\n)(?:^[ \t]*\|[-:\s|]+\|[ \t]*\n)(?:^[ \t]*\|.+\|[ \t]*\n?)+)",
        re.MULTILINE,
    )
    _HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    _CODE_BLOCK_RE = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)

    @staticmethod
    def _parse_md_table(table_text: str) -> Optional[dict]:
        """Parse a markdown table into a Feishu table element."""
        lines = [l.strip() for l in table_text.strip().split("\n") if l.strip()]
        if len(lines) < 3:
            return None

        def split_line(l: str) -> list[str]:
            return [c.strip() for c in l.strip("|").split("|")]

        headers = split_line(lines[0])
        rows = [split_line(l) for l in lines[2:]]
        columns = [
            {"tag": "column", "name": f"c{i}", "display_name": h, "width": "auto"}
            for i, h in enumerate(headers)
        ]
        return {
            "tag": "table",
            "page_size": len(rows) + 1,
            "columns": columns,
            "rows": [
                {f"c{i}": r[i] if i < len(r) else "" for i in range(len(headers))}
                for r in rows
            ],
        }

    def _build_card_elements(self, content: str) -> list[dict]:
        """Split content into div/markdown + table elements for Feishu card."""
        elements: list[dict] = []
        last_end = 0

        for m in self._TABLE_RE.finditer(content):
            before = content[last_end:m.start()]
            if before.strip():
                elements.extend(self._split_headings(before))
            table = self._parse_md_table(m.group(1))
            elements.append(table or {"tag": "markdown", "content": m.group(1)})
            last_end = m.end()

        remaining = content[last_end:]
        if remaining.strip():
            elements.extend(self._split_headings(remaining))

        return elements or [{"tag": "markdown", "content": content}]

    def _split_headings(self, content: str) -> list[dict]:
        """Split content by headings, converting headings to div elements."""
        protected = content
        code_blocks: list[str] = []

        for m in self._CODE_BLOCK_RE.finditer(content):
            code_blocks.append(m.group(1))
            protected = protected.replace(m.group(1), f"\x00CODE{len(code_blocks)-1}\x00", 1)

        elements: list[dict] = []
        last_end = 0

        for m in self._HEADING_RE.finditer(protected):
            before = protected[last_end:m.start()].strip()
            if before:
                elements.append({"tag": "markdown", "content": before})
            text = m.group(2).strip()
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{text}**",
                },
            })
            last_end = m.end()

        remaining = protected[last_end:].strip()
        if remaining:
            elements.append({"tag": "markdown", "content": remaining})

        # Restore code blocks
        for i, cb in enumerate(code_blocks):
            for el in elements:
                if el.get("tag") == "markdown":
                    el["content"] = el["content"].replace(f"\x00CODE{i}\x00", cb)

        return elements or [{"tag": "markdown", "content": content}]

    @staticmethod
    def _format_time(ms: int) -> str:
        """Format milliseconds to human-readable time string."""
        if ms < 1000:
            return f"{ms}ms"
        if ms < 1000:
            return f"{ms}ms"
        total_seconds = ms / 1000
        if total_seconds < 60:
            return f"{total_seconds:.1f}s"
        minutes = int(total_seconds) // 60
        seconds = total_seconds - minutes * 60
        hours = minutes // 60
        if hours > 0:
            minutes = minutes % 60
            return f"{hours}h{minutes}m"
        return f"{minutes}m{seconds:.0f}s"

    def _build_rich_card(self, content: str, exec_info: ExecutionInfo | None = None, wall_clock_ms: int | None = None) -> dict:
        """Build a rich interactive card with status header.

        When exec_info is provided, the card includes:
        - Model name (blue), context remaining % (grey)
        - Thinking status with timing
        - Response status with timing (orange=generating, green=done)
        - Reasoning section separated by hr from response content

        Args:
            content: Response text content
            exec_info: Optional execution metadata
            wall_clock_ms: Wall-clock elapsed time since message creation (overrides backend timing)

        Returns:
            Feishu interactive card dict
        """
        if not exec_info:
            return {
                "config": {"wide_screen_mode": True},
                "elements": self._build_card_elements(content),
            }

        elements: list[dict] = []

        # 用 wall-clock 时间覆盖后端传来的时间（后端时间会因工具调用等卡住）
        display_time_ms = wall_clock_ms if wall_clock_ms is not None else (exec_info.response_time_ms or exec_info.thinking_time_ms)

        # --- Thinking section ---
        # 思考阶段：只要 is_thinking=True 就显示 header（不要求 reasoning 有内容）
        has_reasoning = exec_info.reasoning and exec_info.reasoning.strip()
        if exec_info.is_thinking or has_reasoning:
            # Thinking header line
            parts: list[str] = []
            percent = exec_info.content_left_percent if exec_info.content_left_percent is not None else 100
            parts.append(f"<font color='grey'>剩余 {percent}%</font>")

            if exec_info.is_thinking:
                time_str = f" ({self._format_time(display_time_ms)})" if display_time_ms else ""
                parts.append(f"💭 不要急，容我想想{time_str}")
            elif exec_info.thinking_time_ms is not None:
                parts.append(f"💭 想好了 ({self._format_time(exec_info.thinking_time_ms)})")

            elements.append({
                "tag": "div",
                "text": {
                    "content": "  <font color='grey'>|</font>  ".join(parts),
                    "tag": "lark_md",
                },
            })

            # Reasoning content (simplified markdown for stability)
            if has_reasoning:
                elements.append({"tag": "markdown", "content": exec_info.reasoning.strip()})
                elements.append({"tag": "hr"})

        # --- Response section ---
        response_parts: list[str] = []
        percent = exec_info.content_left_percent if exec_info.content_left_percent is not None else 100
        response_parts.append(f"<font color='grey'>剩余 {percent}%</font>")

        if exec_info.is_generating:
            time_str = f" ({self._format_time(display_time_ms)})" if display_time_ms else ""
            response_parts.append(f"<font color='orange'>📝 回复中{time_str}</font>")
        elif not exec_info.is_thinking:
            # 已完成（不在思考也不在回复）
            done_time = display_time_ms or exec_info.response_time_ms
            time_str = f" ({self._format_time(done_time)})" if done_time else ""
            response_parts.append(f"<font color='green'>✅ 已完成{time_str}</font>")

        if response_parts:
            elements.append({
                "tag": "div",
                "text": {
                    "content": "  <font color='grey'>|</font>  ".join(response_parts),
                    "tag": "lark_md",
                },
            })

        # Response content
        if content and content.strip():
            elements.append({"tag": "hr"})
            elements.extend(self._build_card_elements(content))
            elements.append({"tag": "hr"})

        # Model name footer (right-aligned small text)
        if exec_info.model_name:
            elements.append({
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "transparent",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "elements": [],
                    },
                    {
                        "tag": "column",
                        "width": "auto",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"<font color='grey'>当前模型: {exec_info.model_name}</font>",
                                "text_align": "right",
                            },
                        ],
                    },
                ],
            })

        return {
            "config": {"wide_screen_mode": True},
            "elements": elements or [{"tag": "markdown", "content": content or "(空响应)"}],
        }

    @staticmethod
    def _build_error_card(error_message: str) -> dict:
        """Build an error display card."""
        return {
            "config": {"wide_screen_mode": True},
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": "<font color='red'>⚠️ 处理失败</font>",
                        "tag": "lark_md",
                    },
                },
                {"tag": "markdown", "content": str(error_message)},
            ],
        }

    # File type mappings
    _IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".tiff", ".tif"}
    _AUDIO_EXTS = {".opus"}
    _FILE_TYPE_MAP = {
        ".opus": "opus", ".mp4": "mp4", ".pdf": "pdf", ".doc": "doc", ".docx": "doc",
        ".xls": "xls", ".xlsx": "xls", ".ppt": "ppt", ".pptx": "ppt",
    }

    def _upload_image_sync(self, file_path: str) -> Optional[str]:
        """Upload an image to Feishu and return the image_key."""
        try:
            with open(file_path, "rb") as f:
                request = CreateImageRequest.builder() \
                    .request_body(
                        CreateImageRequestBody.builder()
                        .image_type("message")
                        .image(f)
                        .build()
                    ).build()
                response = self._client.im.v1.image.create(request)
                if response.success():
                    image_key = response.data.image_key
                    logger.debug(f"Uploaded image {os.path.basename(file_path)}: {image_key}")
                    return image_key
                else:
                    logger.error(f"Failed to upload image: code={response.code}, msg={response.msg}")
                    return None
        except Exception as e:
            logger.error(f"Error uploading image {file_path}: {e}")
            return None

    def _upload_file_sync(self, file_path: str) -> Optional[str]:
        """Upload a file to Feishu and return the file_key."""
        ext = os.path.splitext(file_path)[1].lower()
        file_type = self._FILE_TYPE_MAP.get(ext, "stream")
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, "rb") as f:
                request = CreateFileRequest.builder() \
                    .request_body(
                        CreateFileRequestBody.builder()
                        .file_type(file_type)
                        .file_name(file_name)
                        .file(f)
                        .build()
                    ).build()
                response = self._client.im.v1.file.create(request)
                if response.success():
                    file_key = response.data.file_key
                    logger.debug(f"Uploaded file {file_name}: {file_key}")
                    return file_key
                else:
                    logger.error(f"Failed to upload file: code={response.code}, msg={response.msg}")
                    return None
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            return None

    def _download_image_sync(self, message_id: str, image_key: str) -> tuple[Optional[bytes], Optional[str]]:
        """Download an image from Feishu message."""
        try:
            request = GetMessageResourceRequest.builder() \
                .message_id(message_id) \
                .file_key(image_key) \
                .type("image") \
                .build()
            response = self._client.im.v1.message_resource.get(request)
            if response.success():
                file_data = response.file
                if hasattr(file_data, 'read'):
                    file_data = file_data.read()
                return file_data, response.file_name
            else:
                logger.error(f"Failed to download image: code={response.code}, msg={response.msg}")
                return None, None
        except Exception as e:
            logger.error(f"Error downloading image {image_key}: {e}")
            return None, None

    def _download_file_sync(
        self, message_id: str, file_key: str, resource_type: str = "file"
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Download a file/audio/media from a Feishu message."""
        try:
            # Feishu API type param only accepts "image" or "file"
            api_type = "image" if resource_type == "image" else "file"
            request = GetMessageResourceRequest.builder() \
                .message_id(message_id) \
                .file_key(file_key) \
                .type(api_type) \
                .build()
            response = self._client.im.v1.message_resource.get(request)
            if response.success():
                file_data = response.file
                if hasattr(file_data, "read"):
                    file_data = file_data.read()
                return file_data, response.file_name
            else:
                logger.error(f"Failed to download {resource_type}: code={response.code}, msg={response.msg}")
                return None, None
        except Exception as e:
            logger.error(f"Error downloading {resource_type} {file_key}: {e}")
            return None, None

    async def _download_and_save_media(
        self,
        msg_type: str,
        content_json: dict,
        message_id: Optional[str] = None
    ) -> tuple[Optional[str], str]:
        """Download media from Feishu and save to local disk.

        Args:
            msg_type: Message type (image, audio, file, media)
            content_json: Parsed message content
            message_id: Feishu message ID

        Returns:
            (file_path, content_text) - file_path is None if download failed
        """
        loop = asyncio.get_running_loop()
        from iflow_bot.utils.helpers import get_workspace_dir
        media_dir = get_workspace_dir() / "images"
        media_dir.mkdir(parents=True, exist_ok=True)

        data: Optional[bytes] = None
        filename: Optional[str] = None

        if msg_type == "image":
            image_key = content_json.get("image_key")
            if image_key and message_id:
                data, filename = await loop.run_in_executor(
                    None, self._download_image_sync, message_id, image_key
                )
                if not filename:
                    filename = f"{image_key[:16]}.jpg"

        elif msg_type in ("audio", "file", "media"):
            file_key = content_json.get("file_key")
            if file_key and message_id:
                data, filename = await loop.run_in_executor(
                    None, self._download_file_sync, message_id, file_key, msg_type
                )
                if not filename:
                    ext = {"audio": ".opus", "media": ".mp4"}.get(msg_type, "")
                    filename = f"{file_key[:16]}{ext}"

        if data and filename:
            file_path = media_dir / filename
            file_path.write_bytes(data)
            logger.debug(f"Downloaded {msg_type} to {file_path}")
            return str(file_path), f"[{msg_type}: {filename}]"

        return None, f"[{msg_type}: download failed]"

    def _speech_to_text_sync(self, audio_path: str) -> Optional[str]:
        """Convert audio file to text using Feishu speech_to_text API.

        Args:
            audio_path: Path to the audio file (.opus, .wav, .mp3, etc.)

        Returns:
            Recognized text, or None if failed
        """
        import base64
        try:
            audio_data = Path(audio_path).read_bytes()
            speech_b64 = base64.standard_b64encode(audio_data).decode("utf-8")

            ext = Path(audio_path).suffix.lstrip(".")
            fmt = ext if ext else "opus"

            request = FileRecognizeSpeechRequest.builder().request_body(
                FileRecognizeSpeechRequestBody.builder()
                .speech(Speech.builder().speech(speech_b64).build())
                .config(
                    FileConfig.builder()
                    .file_id(Path(audio_path).name)
                    .format(fmt)
                    .engine_type("16k_auto")
                    .build()
                )
                .build()
            ).build()

            response = self._client.speech_to_text.v1.speech.file_recognize(request)
            if response.success():
                text = response.data.recognition_text if response.data else None
                if text:
                    logger.info(f"STT success: {Path(audio_path).name} -> {len(text)} chars")
                    return text
                logger.warning(f"STT returned empty text for {audio_path}")
                return None
            else:
                logger.error(
                    f"STT failed: code={response.code}, msg={response.msg}, "
                    f"log_id={response.get_log_id()}"
                )
                return None
        except Exception as e:
            logger.error(f"STT error for {audio_path}: {e}")
            return None

    def _push_follow_up_sync(self, message_id: str, suggestions: list[str]) -> bool:
        """Push follow-up suggestions for a bot message.

        Args:
            message_id: The bot message ID to attach suggestions to
            suggestions: List of suggestion texts (max 10, each max 200 chars)

        Returns:
            True if successful
        """
        try:
            follow_ups = [
                FollowUp.builder().content(text[:200]).build()
                for text in suggestions[:10]
            ]
            request = PushFollowUpMessageRequest.builder() \
                .message_id(message_id) \
                .request_body(
                    PushFollowUpMessageRequestBody.builder()
                    .follow_ups(follow_ups)
                    .build()
                ).build()

            response = self._client.im.v1.message.push_follow_up(request)
            if response.success():
                logger.debug(f"Push follow_up OK: {message_id}, {len(suggestions)} suggestions")
                return True
            else:
                logger.warning(
                    f"Push follow_up failed: code={response.code}, msg={response.msg}"
                )
                return False
        except Exception as e:
            logger.error(f"Push follow_up error: {e}")
            return False

    def _send_message_sync(
        self, receive_id_type: str, receive_id: str, msg_type: str, content: str
    ) -> Optional[str]:
        """Send a single message (text/image/file/interactive) synchronously."""
        try:
            request = CreateMessageRequest.builder() \
                .receive_id_type(receive_id_type) \
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(receive_id)
                    .msg_type(msg_type)
                    .content(content)
                    .build()
                ).build()
            response = self._client.im.v1.message.create(request)
            if not response.success():
                logger.error(
                    f"Failed to send Feishu {msg_type} message: code={response.code}, "
                    f"msg={response.msg}, log_id={response.get_log_id()}"
                )
                return None

            message_id = None
            data = getattr(response, "data", None)
            if data is not None:
                message_id = getattr(data, "message_id", None)
                if message_id is None and isinstance(data, dict):
                    message_id = data.get("message_id")

            logger.debug(f"Feishu {msg_type} message sent to {receive_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error sending Feishu {msg_type} message: {e}")
            return None

    def _patch_message_sync(self, message_id: str, content: str) -> bool:
        """Patch an existing Feishu message content synchronously."""
        try:
            request = PatchMessageRequest.builder() \
                .message_id(message_id) \
                .request_body(
                    PatchMessageRequestBody.builder()
                    .content(content)
                    .build()
                ).build()
            response = self._client.im.v1.message.patch(request)
            if not response.success():
                logger.error(
                    f"Failed to patch Feishu message: code={response.code}, "
                    f"msg={response.msg}, log_id={response.get_log_id()}"
                )
                return False
            return True
        except Exception as e:
            logger.error(f"Error patching Feishu message {message_id}: {e}")
            return False

    async def _send_text_fallback(
        self, receive_id_type: str, receive_id: str, content: str, stream_key: Optional[str] = None
    ) -> bool:
        """Fallback to plain text when streaming card delivery fails."""
        if not content.strip():
            return False

        loop = asyncio.get_running_loop()
        payload = json.dumps({"text": content}, ensure_ascii=False)
        content_len = len(content)
        created_id = await loop.run_in_executor(
            None, self._send_message_sync,
            receive_id_type, receive_id, "text", payload
        )
        if created_id:
            if stream_key:
                self._streaming_last_content[stream_key] = content
            logger.warning(
                "Feishu streaming degraded to text fallback: stream_key=%s receive_id=%s content_len=%d",
                stream_key or receive_id,
                receive_id,
                content_len,
            )
            return True
        logger.error(
            "Feishu text fallback send failed: stream_key=%s receive_id=%s content_len=%d",
            stream_key or receive_id,
            receive_id,
            content_len,
        )
        return False

    async def _handle_streaming_message(
        self, msg: OutboundMessage, receive_id_type: str
    ) -> None:
        """Handle Feishu streaming message by create+patch interactive card."""
        stream_key = msg.chat_id
        loop = asyncio.get_running_loop()

        if msg.metadata.get("_streaming_end"):
            source_message_id = msg.metadata.get("reply_to_id")
            if source_message_id:
                await self._remove_typing_reaction(source_message_id)
            self._streaming_message_ids.pop(stream_key, None)
            self._streaming_last_content.pop(stream_key, None)
            self._streaming_start_time.pop(stream_key, None)
            logger.debug(f"Feishu streaming ended: {stream_key}")
            return

        content = (msg.content or "").strip()
        if not content:
            logger.debug(f"Feishu streaming skip empty content: {stream_key}")
            return

        content_len = len(content)
        # 内容相同时通常跳过，但如果是最终消息（is_generating=False）则仍需 patch 以更新 header 状态
        is_final = msg.execution_info and not msg.execution_info.is_generating
        if self._streaming_last_content.get(stream_key) == content and not is_final:
            logger.debug(f"Feishu streaming skip duplicate content: {stream_key} len={content_len}")
            return

        source_message_id = msg.metadata.get("reply_to_id")
        if source_message_id:
            await self._remove_typing_reaction(source_message_id)

        # wall-clock 计时：记录首次消息时间，每次 patch 用当前时间减去起点
        if stream_key not in self._streaming_start_time:
            self._streaming_start_time[stream_key] = time.time()
        wall_clock_ms = int((time.time() - self._streaming_start_time[stream_key]) * 1000)

        # 流式阶段使用 rich card 显示状态 header（模型名、思考/回复耗时等）
        card = self._build_rich_card(content, msg.execution_info, wall_clock_ms=wall_clock_ms)
        card_content = json.dumps(card, ensure_ascii=False)

        message_id = self._streaming_message_ids.get(stream_key)
        if message_id:
            logger.debug(
                "Feishu streaming patch attempt: stream_key=%s message_id=%s content_len=%d",
                stream_key,
                message_id,
                content_len,
            )
            patched = await asyncio.wait_for(
                loop.run_in_executor(None, self._patch_message_sync, message_id, card_content),
                timeout=self._API_TIMEOUT,
            )
            if patched:
                self._streaming_last_content[stream_key] = content
                logger.debug(
                    "Feishu streaming patched: stream_key=%s message_id=%s content_len=%d",
                    stream_key,
                    message_id,
                    content_len,
                )
                # Push follow-up suggestions after final streaming patch
                if is_final:
                    suggestions = (msg.metadata or {}).get("follow_up_suggestions")
                    if suggestions and isinstance(suggestions, list):
                        await loop.run_in_executor(
                            None, self._push_follow_up_sync, message_id, suggestions
                        )
                return
            self._streaming_message_ids.pop(stream_key, None)
            logger.warning(
                "Feishu streaming patch failed, recreating: stream_key=%s message_id=%s content_len=%d",
                stream_key,
                message_id,
                content_len,
            )

        logger.debug(
            "Feishu streaming create attempt: stream_key=%s receive_id=%s content_len=%d",
            stream_key,
            msg.chat_id,
            content_len,
        )
        created_id = await asyncio.wait_for(
            loop.run_in_executor(
                None, self._send_message_sync,
                receive_id_type, msg.chat_id, "interactive", card_content
            ),
            timeout=self._API_TIMEOUT,
        )
        if created_id:
            self._streaming_message_ids[stream_key] = created_id
            self._streaming_last_content[stream_key] = content
            logger.info(
                "Feishu streaming placeholder sent: stream_key=%s message_id=%s content_len=%d",
                stream_key,
                created_id,
                content_len,
            )
            return

        logger.error(
            "Feishu streaming placeholder send failed: stream_key=%s receive_id=%s content_len=%d",
            stream_key,
            msg.chat_id,
            content_len,
        )
        await self._send_text_fallback(receive_id_type, msg.chat_id, content, stream_key=stream_key)

    def _add_reaction_sync(self, message_id: str, emoji_type: str) -> Optional[str]:
        """Sync helper for adding reaction (runs in thread pool)."""
        try:
            request = CreateMessageReactionRequest.builder() \
                .message_id(message_id) \
                .request_body(
                    CreateMessageReactionRequestBody.builder()
                    .reaction_type(Emoji.builder().emoji_type(emoji_type).build())
                    .build()
                ).build()

            response = self._client.im.v1.message_reaction.create(request)

            if not response.success():
                logger.warning(f"Failed to add reaction: code={response.code}, msg={response.msg}")
                return None

            reaction_id = None
            data = getattr(response, "data", None)
            if data is not None:
                reaction_id = getattr(data, "reaction_id", None)
                if reaction_id is None and isinstance(data, dict):
                    reaction_id = data.get("reaction_id")
            logger.debug(f"Added {emoji_type} reaction to message {message_id}")
            return reaction_id
        except Exception as e:
            logger.warning(f"Error adding reaction: {e}")
            return None

    def _delete_reaction_sync(self, message_id: str, reaction_id: str) -> bool:
        """Sync helper for deleting reaction (runs in thread pool)."""
        try:
            request = DeleteMessageReactionRequest.builder() \
                .message_id(message_id) \
                .reaction_id(reaction_id) \
                .build()
            response = self._client.im.v1.message_reaction.delete(request)
            if not response.success():
                logger.warning(
                    f"Failed to delete reaction: code={response.code}, msg={response.msg}"
                )
                return False
            logger.debug(f"Deleted reaction from message {message_id}")
            return True
        except Exception as e:
            logger.warning(f"Error deleting reaction: {e}")
            return False

    async def _add_reaction(self, message_id: str, emoji_type: str = "THUMBSUP") -> Optional[str]:
        """Add a reaction emoji to a message (non-blocking).

        Common emoji types: THUMBSUP, OK, EYES, DONE, OnIt, HEART
        """
        if not self._client or not Emoji:
            return None

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._add_reaction_sync, message_id, emoji_type)

    async def _remove_typing_reaction(self, source_message_id: str) -> None:
        """Remove the pending typing reaction from a source message."""
        reaction_id = self._typing_reaction_ids.pop(source_message_id, None)
        self._typing_reaction_timestamps.pop(source_message_id, None)
        if not reaction_id:
            return

        loop = asyncio.get_running_loop()
        deleted = await loop.run_in_executor(
            None, self._delete_reaction_sync, source_message_id, reaction_id
        )
        if deleted:
            logger.debug(f"Typing reaction cleared: {source_message_id}")

    async def _cleanup_stale_reactions(self) -> None:
        """Remove typing reactions that are older than 5 minutes (likely from crashed processing)."""
        now = time.time()
        stale_ids = [
            msg_id for msg_id, ts in self._typing_reaction_timestamps.items()
            if now - ts > 300
        ]
        for msg_id in stale_ids:
            await self._remove_typing_reaction(msg_id)
            self._typing_reaction_timestamps.pop(msg_id, None)

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message through Feishu, including media (images/files) if present.

        Supports:
        - Text messages (converted to interactive cards)
        - Image messages
        - File messages
        - Audio messages

        Args:
            msg: OutboundMessage to send
        """
        if not self._client:
            logger.warning("Feishu client not initialized")
            return

        try:
            # Determine receive_id_type based on chat_id prefix
            receive_id_type = "chat_id" if msg.chat_id.startswith("oc_") else "open_id"
            loop = asyncio.get_running_loop()

            if msg.metadata.get("_streaming") or msg.metadata.get("_streaming_end"):
                await self._handle_streaming_message(msg, receive_id_type)
                return

            if msg.metadata.get("_progress"):
                return

            source_message_id = msg.metadata.get("reply_to_id")
            if source_message_id:
                await self._remove_typing_reaction(source_message_id)

            self._streaming_message_ids.pop(msg.chat_id, None)
            self._streaming_last_content.pop(msg.chat_id, None)
            self._streaming_start_time.pop(msg.chat_id, None)

            # Handle media files first
            media = getattr(msg, 'media', None) or []
            for file_path in media:
                if not os.path.isfile(file_path):
                    logger.warning(f"Media file not found: {file_path}")
                    continue
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self._IMAGE_EXTS:
                    key = await asyncio.wait_for(
                        loop.run_in_executor(None, self._upload_image_sync, file_path),
                        timeout=self._API_TIMEOUT,
                    )
                    if key:
                        await asyncio.wait_for(
                            loop.run_in_executor(
                                None, self._send_message_sync,
                                receive_id_type, msg.chat_id, "image",
                                json.dumps({"image_key": key}, ensure_ascii=False),
                            ),
                            timeout=self._API_TIMEOUT,
                        )
                else:
                    key = await asyncio.wait_for(
                        loop.run_in_executor(None, self._upload_file_sync, file_path),
                        timeout=self._API_TIMEOUT,
                    )
                    if key:
                        media_type = "audio" if ext in self._AUDIO_EXTS else "file"
                        await asyncio.wait_for(
                            loop.run_in_executor(
                                None, self._send_message_sync,
                                receive_id_type, msg.chat_id, media_type,
                                json.dumps({"file_key": key}, ensure_ascii=False),
                            ),
                            timeout=self._API_TIMEOUT,
                        )

            # Send text content as interactive card (with rich header if ExecutionInfo present)
            if msg.content and msg.content.strip():
                if msg.metadata.get("_error"):
                    card = self._build_error_card(msg.content)
                    await asyncio.wait_for(
                        loop.run_in_executor(
                            None, self._send_message_sync,
                            receive_id_type, msg.chat_id, "interactive",
                            json.dumps(card, ensure_ascii=False),
                        ),
                        timeout=self._API_TIMEOUT,
                    )
                else:
                    final_wall_ms = None
                    start_t = self._streaming_start_time.get(msg.chat_id)
                    if start_t:
                        final_wall_ms = int((time.time() - start_t) * 1000)
                    card = self._build_rich_card(msg.content, msg.execution_info, wall_clock_ms=final_wall_ms)
                    sent_msg_id = await asyncio.wait_for(
                        loop.run_in_executor(
                            None, self._send_message_sync,
                            receive_id_type, msg.chat_id, "interactive",
                            json.dumps(card, ensure_ascii=False),
                        ),
                        timeout=self._API_TIMEOUT,
                    )

                    # Push follow-up suggestions for completed (non-streaming) replies
                    is_done = msg.execution_info and not msg.execution_info.is_generating and not msg.execution_info.is_thinking
                    if sent_msg_id and is_done:
                        suggestions = msg.metadata.get("follow_up_suggestions")
                        if suggestions and isinstance(suggestions, list):
                            await loop.run_in_executor(
                                None, self._push_follow_up_sync, sent_msg_id, suggestions
                            )

        except Exception as e:
            # 清理可能残留的流式状态，防止内存泄漏
            if hasattr(msg, 'chat_id') and msg.chat_id:
                self._streaming_message_ids.pop(msg.chat_id, None)
                self._streaming_last_content.pop(msg.chat_id, None)
                self._streaming_start_time.pop(msg.chat_id, None)
            logger.error(f"Error sending Feishu message: {e}")

    def _on_reaction_created_sync(self, data: "P2ImMessageReactionCreatedV1") -> None:
        """Handle message reaction created event (no-op, just to suppress errors)."""
        pass

    def _on_reaction_deleted_sync(self, data: "P2ImMessageReactionDeletedV1") -> None:
        """Handle message reaction deleted event (no-op, just to suppress errors)."""
        pass

    def _on_message_read_sync(self, data: "P2ImMessageMessageReadV1") -> None:
        """Handle read receipt events (no-op, just to suppress SDK noise)."""
        pass

    def _on_bot_p2p_chat_entered_sync(self, data: "P2ImChatAccessEventBotP2pChatEnteredV1") -> None:
        """Handle bot access events (no-op, just to suppress SDK noise)."""
        pass

    def _on_message_recalled_sync(self, data: "P2ImMessageRecalledV1") -> None:
        """Handle message recalled event — forward to bus so loop can cancel processing."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._on_message_recalled(data), self._loop)

    async def _on_message_recalled(self, data: "P2ImMessageRecalledV1") -> None:
        """Process message recall: publish a special inbound message to cancel active task."""
        try:
            event = data.event
            message_id = event.message_id
            chat_id = event.chat_id
            logger.info(f"Feishu message recalled: message_id={message_id} chat_id={chat_id}")

            # Determine reply_to (same logic as _on_message — use chat_id for group, sender for private)
            # For recall events we don't have chat_type, so we check if chat_id looks like a group
            # Actually chat_id from recall event is the chat_id, which is the conversation ID
            # We need to figure out the reply_to used for this message
            # Since we use unified session, just publish with chat_id
            await self.bus.publish_inbound(
                InboundMessage(
                    channel="feishu",
                    sender_id="system",
                    chat_id=chat_id or "",
                    content="",
                    metadata={
                        "_recalled": True,
                        "recalled_message_id": message_id,
                    },
                )
            )
        except Exception as e:
            logger.error(f"Error processing Feishu recall event: {e}")

    def _on_message_sync(self, data: "P2ImMessageReceiveV1") -> None:
        """Sync handler for incoming messages (called from WebSocket thread).

        Schedules async handling in the main event loop.
        """
        if self._loop and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._on_message(data), self._loop)
            future.add_done_callback(self._on_message_future_done)

    @staticmethod
    def _on_message_future_done(future) -> None:
        exc = future.exception()
        if exc:
            logger.error(f"Unhandled error in _on_message: {exc}")

    async def _on_message(self, data: "P2ImMessageReceiveV1") -> None:
        """Handle incoming message from Feishu.

        Processes message content, downloads media if present,
        and publishes to message bus.
        """
        await self._cleanup_stale_reactions()

        try:
            event = data.event
            message = event.message
            sender = event.sender

            # Deduplication check
            message_id = message.message_id
            if message_id in self._processed_message_ids:
                return
            self._processed_message_ids[message_id] = None

            # Trim cache (keep last 1000 messages)
            while len(self._processed_message_ids) > 1000:
                self._processed_message_ids.popitem(last=False)

            # Skip bot messages
            if sender.sender_type == "bot":
                return

            sender_id = sender.sender_id.open_id if sender.sender_id else "unknown"
            chat_id = message.chat_id
            chat_type = message.chat_type
            msg_type = message.message_type

            # Skip system messages (e.g. "你撤回了一条消息重新编辑")
            if msg_type == "system":
                logger.debug(f"Skipping system message: message_id={message_id}")
                return

            # 秒回"敲键盘"反应，作为处理中提示
            typing_reaction_id = await self._add_reaction(message_id, "OnIt")
            if typing_reaction_id:
                self._typing_reaction_ids[message_id] = typing_reaction_id
                self._typing_reaction_timestamps[message_id] = time.time()

            # Parse content
            content_parts: list[str] = []
            media_paths: list[str] = []

            try:
                content_json = json.loads(message.content) if message.content else {}
            except json.JSONDecodeError:
                content_json = {}

            if msg_type == "text":
                text = content_json.get("text", "")
                if text:
                    content_parts.append(text)

            elif msg_type == "post":
                text_parts, resources = _extract_post_parts(content_json)
                if text_parts:
                    content_parts.extend(text_parts)
                if resources:
                    async def _download_resource(resource):
                        resource_type = resource.get("type")
                        if resource_type == "image":
                            return await self._download_and_save_media("image", resource, message_id)
                        elif resource_type in ("file", "media", "audio"):
                            return await self._download_and_save_media(resource_type, resource, message_id)
                        else:
                            return None, f"[{resource_type}]"

                    results = await asyncio.gather(
                        *[_download_resource(r) for r in resources],
                        return_exceptions=True,
                    )
                    for result in results:
                        if isinstance(result, Exception):
                            logger.warning(f"Media download failed: {result}")
                            continue
                        file_path, content_text = result
                        if file_path:
                            media_paths.append(file_path)
                        if content_text:
                            content_parts.append(content_text)

            elif msg_type in ("image", "audio", "file", "media"):
                file_path, content_text = await self._download_and_save_media(
                    msg_type, content_json, message_id
                )
                if file_path and msg_type == "audio":
                    # Try speech-to-text for audio messages
                    loop = asyncio.get_running_loop()
                    recognized = await loop.run_in_executor(
                        None, self._speech_to_text_sync, file_path
                    )
                    if recognized:
                        content_parts.append(f"[语音转文字] {recognized}")
                    else:
                        # STT failed, still pass file path for reference
                        media_paths.append(file_path)
                        content_parts.append(content_text)
                elif file_path:
                    media_paths.append(file_path)
                    content_parts.append(content_text)
                else:
                    content_parts.append(content_text)

            elif msg_type in ("share_chat", "share_user", "interactive",
                            "share_calendar_event", "system", "merge_forward"):
                text = _extract_share_card_content(content_json, msg_type)
                if text:
                    content_parts.append(text)

            else:
                content_parts.append(MSG_TYPE_MAP.get(msg_type, f"[{msg_type}]"))

            content = "\n".join(content_parts) if content_parts else ""

            if not content and not media_paths:
                return

            # Determine reply target: group chat uses chat_id, private uses sender_id
            reply_to = chat_id if chat_type == "group" else sender_id

            logger.info(
                "Feishu inbound accepted: message_id=%s chat_type=%s msg_type=%s sender=%s reply_to=%s content_len=%d media=%d",
                message_id,
                chat_type,
                msg_type,
                sender_id,
                reply_to,
                len(content),
                len(media_paths),
            )

            # Forward to message bus
            await self._handle_message(
                sender_id=sender_id,
                chat_id=reply_to,
                content=content,
                media=media_paths,
                metadata={
                    "message_id": message_id,
                    "chat_type": chat_type,
                    "msg_type": msg_type,
                }
            )

        except Exception as e:
            logger.error(f"Error processing Feishu message: {e}")
