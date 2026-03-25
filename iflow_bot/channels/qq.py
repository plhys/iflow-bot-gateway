"""QQ channel implementation using qq-botpy SDK.

使用 qq-botpy SDK 通过 WebSocket 连接 QQ 频道机器人。
支持 C2C 私聊消息和 QQ 群消息。
"""

import asyncio
import logging
import time
from collections import deque
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

import aiohttp

from iflow_bot.bus.events import OutboundMessage
from iflow_bot.bus.queue import MessageBus
from iflow_bot.channels.base import BaseChannel
from iflow_bot.channels.manager import register_channel
from iflow_bot.config.schema import QQConfig

try:
    import botpy
    from botpy.message import C2CMessage, GroupMessage
    QQ_AVAILABLE = True
except ImportError:
    QQ_AVAILABLE = False
    botpy = None  # type: ignore
    C2CMessage = None  # type: ignore
    GroupMessage = None  # type: ignore

if TYPE_CHECKING:
    from botpy.message import C2CMessage, GroupMessage


logger = logging.getLogger(__name__)


def _extract_image_urls(attachments: Any) -> list[str]:
    urls: list[str] = []
    if not attachments:
        return urls
    for attachment in attachments:
        content_type = getattr(attachment, "content_type", "") or ""
        url = getattr(attachment, "url", "") or ""
        if content_type.startswith("image/") and url:
            urls.append(url)
    return urls


async def _download_image(url: str, save_dir: Path) -> Optional[str]:
    try:
        save_dir.mkdir(parents=True, exist_ok=True)
        filename = f"image_{int(time.time() * 1000)}.png"
        filepath = save_dir / filename
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.warning(f"[QQ] Failed to download image: HTTP {response.status}")
                    return None
                with open(filepath, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        logger.info(f"[QQ] Image downloaded: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"[QQ] Error downloading image: {e}")
        return None


def _append_image_prompt(content: str, image_path: str) -> str:
    prompt = (
        "\n\n[用户发送了图片，路径: "
        f"{image_path}"
        "。请用简洁自然的语言描述图片内容，1-2句话概括即可，就像朋友聊天一样。]"
    )
    return f"{content}{prompt}" if content else prompt.strip()


def _make_bot_class(channel: "QQChannel") -> Any:
    """创建绑定到指定 Channel 的 botpy.Client 子类。"""
    intents = botpy.Intents(public_messages=True, direct_message=True)

    class _Bot(botpy.Client):
        def __init__(self):
            super().__init__(intents=intents)

        async def on_ready(self):
            logger.info(f"[{channel.name}] QQ bot ready: {self.robot.name}")

        async def on_c2c_message_create(self, message: "C2CMessage"):
            await channel._on_c2c_message(message)

        async def on_group_at_message_create(self, message: "GroupMessage"):
            await channel._on_group_message(message)

    return _Bot


@register_channel("qq")
class QQChannel(BaseChannel):
    """QQ Channel - 使用 qq-botpy SDK 通过 WebSocket 连接。

    支持:
    - C2C 私聊消息
    - QQ 群 @机器人消息

    要求:
    - app_id: QQ 机器人 AppID
    - secret: QQ 机器人 Secret

    Attributes:
        name: 渠道名称 ("qq")
        config: QQ 配置对象
        bus: 消息总线实例
        _client: botpy Client 实例
        _processed_ids: 已处理消息 ID 队列 (去重)
        _group_msg_seq: 群消息序号计数器
    """

    name = "qq"

    def __init__(self, config: QQConfig, bus: MessageBus):
        """初始化 QQ Channel。

        Args:
            config: QQ 配置对象
            bus: 消息总线实例
        """
        super().__init__(config, bus)
        self.config: QQConfig = config
        self._client: Any = None
        self._processed_ids: deque = deque(maxlen=1000)
        self._group_msg_seq: dict[str, int] = {}  # 群消息序号计数器

    async def start(self) -> None:
        """启动 QQ Bot。"""
        if not QQ_AVAILABLE:
            logger.error(
                f"[{self.name}] QQ SDK not installed. Run: pip install qq-botpy"
            )
            return

        if not self.config.app_id or not self.config.secret:
            logger.error(f"[{self.name}] app_id and secret not configured")
            return

        # 加载持久化的 msg_seq 状态
        await self._load_msg_seq_state()

        self._running = True
        BotClass = _make_bot_class(self)
        self._client = BotClass()

        logger.info(f"[{self.name}] QQ bot started (C2C + Group)")
        await self._run_bot()

    async def _run_bot(self) -> None:
        """运行 Bot 连接，支持自动重连。"""
        while self._running:
            try:
                await self._client.start(
                    appid=self.config.app_id,
                    secret=self.config.secret
                )
            except Exception as e:
                logger.warning(f"[{self.name}] QQ bot error: {e}")
            finally:
                # 连接断开时保存 msg_seq 状态
                await self._save_msg_seq_state()
            if self._running:
                logger.info(f"[{self.name}] Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """停止 QQ Bot。"""
        self._running = False
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
        
        # 保存 msg_seq 状态
        await self._save_msg_seq_state()
        
        logger.info(f"[{self.name}] QQ bot stopped")

    async def _load_msg_seq_state(self):
        """从文件加载 msg_seq 计数器状态"""
        state_file = Path.home() / ".iflow-bot" / "qq_msg_seq_state.json"
        try:
            if state_file.exists():
                import json
                with open(state_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)

                # 迁移旧格式：如果加载的数据是纯数字字典，转换为新格式
                # 旧格式：{"D35E1F44...": 5} 直接存储群 ID
                # 新格式：{"group_D35E1F44...": 5, "group_D35E1F44..._thinking": 1005}
                self._group_msg_seq = {}
                for key, value in loaded_data.items():
                    if not key.startswith("group_"):
                        # 旧格式，转换为新格式
                        self._group_msg_seq[f"group_{key}"] = value
                        logger.info(f"[{self.name}] Migrated old seq key '{key}' -> 'group_{key}' = {value}")
                    else:
                        self._group_msg_seq[key] = value

                logger.info(f"[{self.name}] Loaded msg_seq state: {len(self._group_msg_seq)} counters")
                for k, v in self._group_msg_seq.items():
                    logger.debug(f"[{self.name}]   {k}: {v}")
            else:
                logger.info(f"[{self.name}] No msg_seq state file found, starting fresh")
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to load msg_seq state: {e}")
            self._group_msg_seq = {}
    
    async def _save_msg_seq_state(self):
        """保存 msg_seq 计数器状态到文件"""
        state_file = Path.home() / ".iflow-bot" / "qq_msg_seq_state.json"
        try:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self._group_msg_seq, f, ensure_ascii=False, indent=2)
            logger.info(f"[{self.name}] Saved msg_seq state: {len(self._group_msg_seq)} groups")
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to save msg_seq state: {e}")

    async def send(self, msg: OutboundMessage) -> None:
        """通过 QQ 发送消息。

        Args:
            msg: 出站消息对象
                - chat_id: 用户 openid 或群 ID
                - content: 消息内容
                - metadata: 包含 group_id(群聊) 或 openid(私聊)
        """
        logger.warning(f"[{self.name}] [DEBUG] send() called - chat_id={msg.chat_id}, content_len={len(msg.content)}, metadata={msg.metadata}")
        
        if not self._client:
            logger.warning(f"[{self.name}] QQ client not initialized")
            return

        try:
            metadata = msg.metadata or {}
            content = msg.content

            if metadata.get("is_group"):
                # 群聊消息 - 使用被动回复模式
                group_id = metadata.get("group_id")
                msg_id = metadata.get("reply_to_id") or metadata.get("message_id")
                
                logger.warning(f"[{self.name}] [DEBUG] Group message - group_id={group_id}, msg_id={msg_id}, metadata keys={list(metadata.keys())}")
                
                # 获取并递增 msg_seq（使用小整数）
                # msg_seq 必须唯一且递增，不能循环重置，否则会被 QQ 服务器识别为重复消息
                seq_key = f"group_{group_id}"
                if seq_key not in self._group_msg_seq:
                    self._group_msg_seq[seq_key] = 1
                msg_seq = self._group_msg_seq[seq_key]
                self._group_msg_seq[seq_key] += 1
                # 注意：msg_seq 会一直递增（1, 2, 3, ...），永不重置
                # QQ API 要求每个 (msg_id, msg_seq) 组合必须唯一
                # 即使超过 1000 也不会重复使用已用过的值
                
                if self.config.markdown_support:
                    # Markdown 模式
                    logger.warning(f"[{self.name}] [DEBUG] Sending group message to {group_id}, msg_id={msg_id}, msg_seq={msg_seq}, markdown=true")
                    try:
                        # 构建 payload
                        payload = {
                            "msg_type": 2,  # markdown 类型
                            "msg_id": msg_id,
                            "msg_seq": msg_seq,
                            "markdown": {"content": content}
                        }
                        logger.warning(f"[{self.name}] [DEBUG] Payload: {payload}")
                        
                        # 使用底层 HTTP 客户端发送请求
                        from botpy.http import Route
                        route = Route("POST", f"/v2/groups/{group_id}/messages", group_openid=group_id)
                        await self._client.api._http.request(route, json=payload)
                    except Exception as e:
                        logger.error(f"[{self.name}] Error sending Markdown message: {e}")
                        raise
                else:
                    # 纯文本模式
                    logger.debug(f"[{self.name}] Sending group message to {group_id}, msg_id={msg_id}, msg_seq={msg_seq}, markdown=false")
                    await self._client.api.post_group_message(
                        group_openid=group_id,
                        msg_type=0,  # 文本消息类型
                        msg_id=msg_id,
                        msg_seq=msg_seq,
                        content=content,
                    )
            else:
                # 私聊消息
                openid = msg.chat_id
                if self.config.markdown_support:
                    # Markdown 模式：使用底层 HTTP 客户端手动构建 payload
                    logger.debug(f"[{self.name}] Sending C2C message to {openid}, markdown=true")
                    try:
                        # 构建 payload，只包含必要字段
                        payload = {
                            "msg_type": 2,
                            "markdown": {"content": content}
                        }
                        # 私聊消息的 msg_id 和 msg_seq 从 metadata 获取
                        c2c_msg_id = metadata.get("reply_to_id") or metadata.get("message_id")
                        if c2c_msg_id:
                            payload["msg_id"] = c2c_msg_id
                            payload["msg_seq"] = 1  # 私聊消息的 msg_seq 从 1 开始
                        
                        # 使用底层 HTTP 客户端发送请求
                        from botpy.http import Route
                        route = Route("POST", f"/v2/users/{openid}/messages")
                        await self._client.api._http.request(route, json=payload)
                    except Exception as e:
                        logger.error(f"[{self.name}] Error sending Markdown message: {e}")
                        raise
                else:
                    # 纯文本模式
                    logger.debug(f"[{self.name}] Sending C2C message to {openid}, markdown=false")
                    await self._client.api.post_c2c_message(
                        openid=openid,
                        msg_type=0,
                        content=content,
                    )
            logger.debug(f"[{self.name}] Message sent to {msg.chat_id}")
        except Exception as e:
            logger.error(f"[{self.name}] Error sending message: {e}")

    async def _on_c2c_message(self, data: "C2CMessage") -> None:
        """处理来自 QQ 的 C2C 私聊消息。

        Args:
            data: QQ 消息对象
        """
        try:
            # 消息 ID 去重
            if data.id in self._processed_ids:
                return
            self._processed_ids.append(data.id)

            # 提取用户信息
            author = data.author
            user_id = str(
                getattr(author, 'id', None) or
                getattr(author, 'user_openid', 'unknown')
            )

            # 提取消息内容
            content = (data.content or "").strip()

            # 提取图片并下载
            attachments = getattr(data, "attachments", None)
            image_urls = _extract_image_urls(attachments)
            image_path: Optional[str] = None
            if image_urls:
                image_path = await _download_image(
                    image_urls[0],
                    Path.home() / ".iflow-bot" / "workspace" / "images",
                )
                if image_path:
                    content = _append_image_prompt(content, image_path)

            if not content:
                if image_urls:
                    content = "[发送了图片]"
                else:
                    return

            # 先发送 "Thinking..." 提示（非阻塞，不影响主流程）
            try:
                if self._client:
                    await self._client.api.post_c2c_message(
                        openid=user_id,
                        msg_type=0,
                        content="🤔 Thinking...",
                    )
            except Exception as e:
                logger.debug(f"[{self.name}] Failed to send thinking: {e}")

            # 转发到消息总线
            await self._handle_message(
                sender_id=user_id,
                chat_id=user_id,  # 私聊：chat_id == user_id
                content=content,
                metadata={"is_group": False},
            )

        except Exception:
            logger.exception(f"[{self.name}] Error handling C2C message")

    async def _on_group_message(self, data: "GroupMessage") -> None:
        """处理来自 QQ 群的 @机器人消息。

        Args:
            data: QQ 群消息对象
        """
        try:
            # 消息 ID 去重
            if data.id in self._processed_ids:
                return
            self._processed_ids.append(data.id)

            # 检查是否在允许的群列表中
            group_id = data.group_openid or ""
            if self.config.groups and group_id not in self.config.groups:
                logger.warning(f"[{self.name}] Message from unauthorized group: {group_id}")
                return

            # 提取用户信息
            author = data.author
            user_id = str(
                getattr(author, 'member_openid', None) or
                getattr(author, 'user_openid', 'unknown')
            )
            username = user_id

            # 提取消息内容
            content = (data.content or "").strip()

            # 移除 @机器人 的部分
            bot_id = getattr(self._client.robot, 'id', '') if self._client else ''
            if bot_id:
                content = content.replace(f'<@!{bot_id}>', '').strip()
            # 提取图片并下载
            attachments = getattr(data, "attachments", None)
            image_urls = _extract_image_urls(attachments)
            image_path: Optional[str] = None
            if image_urls:
                image_path = await _download_image(
                    image_urls[0],
                    Path.home() / ".iflow-bot" / "workspace" / "images",
                )
                if image_path:
                    content = _append_image_prompt(content, image_path)

            if not content:
                if image_urls:
                    content = "[发送了图片]"
                else:
                    return

            # 发送 "Thinking..." 提示（被动回复模式）
            try:
                if self._client:
                    # 使用独立的 thinking 消息计数器，不和回复消息共用
                    # 从 1000 开始，避免和回复消息（从 1 开始）冲突
                    seq_key = f"group_{group_id}_thinking"
                    if seq_key not in self._group_msg_seq:
                        self._group_msg_seq[seq_key] = 1000
                    thinking_msg_seq = self._group_msg_seq[seq_key]
                    self._group_msg_seq[seq_key] += 1

                    await self._client.api.post_group_message(
                        group_openid=group_id,
                        msg_type=0,
                        content="🤔 Thinking...",
                        msg_id=data.id,
                        msg_seq=thinking_msg_seq,
                    )
            except Exception as e:
                logger.debug(f"[{self.name}] Failed to send thinking: {e}")

            # 转发到消息总线
            chat_id = f"group_{group_id}"
            await self._handle_message(
                sender_id=user_id,
                chat_id=chat_id,
                content=content,
                metadata={
                    "message_id": data.id,  # 保存消息ID用于回复
                    "is_group": True,
                    "group_id": group_id,
                    "username": username,
                },
            )

        except Exception:
            logger.exception(f"[{self.name}] Error handling group message")
