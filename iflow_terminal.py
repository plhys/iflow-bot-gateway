#!/usr/bin/env python3
"""iFlow ACP 终端客户端 — 连接共享 ACP server 的交互式对话终端。

用法:
    python3 iflow_terminal.py              # 默认连接 localhost:8090
    python3 iflow_terminal.py --port 8090  # 指定端口
    python3 iflow_terminal.py --new        # 强制新建会话

快捷命令:
    /new     开始新对话
    /quit    退出
    /status  查看连接状态
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Session persistence
# ---------------------------------------------------------------------------
SESSION_MAP_FILE = Path.home() / ".iflow-bot" / "session_mappings.json"
SESSION_KEY = "unified:default"  # 与 gateway 共享同一个 key


def load_session_id() -> Optional[str]:
    """从 session_mappings.json 读取已有 session ID。"""
    if SESSION_MAP_FILE.exists():
        try:
            data = json.loads(SESSION_MAP_FILE.read_text("utf-8"))
            return data.get(SESSION_KEY)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def save_session_id(session_id: str) -> None:
    """将 session ID 写入 session_mappings.json（与 gateway 共享）。"""
    data: dict = {}
    if SESSION_MAP_FILE.exists():
        try:
            data = json.loads(SESSION_MAP_FILE.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    data[SESSION_KEY] = session_id
    SESSION_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_MAP_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")


# ---------------------------------------------------------------------------
# ACP Client (minimal, self-contained)
# ---------------------------------------------------------------------------
class TerminalACPClient:
    """轻量 ACP 客户端，只做终端交互需要的事。"""

    def __init__(self, host: str = "localhost", port: int = 8090, timeout: int = 300):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._ws = None
        self._request_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._notification_queue: asyncio.Queue = asyncio.Queue()
        self._recv_task: Optional[asyncio.Task] = None
        self.session_id: Optional[str] = None

    @property
    def ws_url(self) -> str:
        return f"ws://{self.host}:{self.port}/acp"

    # -- connection --
    async def connect(self) -> None:
        import websockets
        self._ws = await websockets.connect(
            self.ws_url, ping_interval=30, ping_timeout=10, close_timeout=5,
        )
        self._recv_task = asyncio.create_task(self._recv_loop())
        # 等待 ACP server 准备就绪
        await asyncio.sleep(2)

    async def disconnect(self) -> None:
        if self._recv_task:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()

    # -- low level --
    async def _recv_loop(self) -> None:
        while True:
            try:
                raw = await self._ws.recv()
                if isinstance(raw, str) and not raw.strip().startswith("{"):
                    continue  # skip //ready, //stderr etc.
                msg = json.loads(raw)
                if "id" in msg:
                    rid = msg["id"]
                    fut = self._pending.pop(rid, None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    await self._notification_queue.put(msg)
            except asyncio.CancelledError:
                break
            except Exception:
                break

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _request(self, method: str, params: dict, timeout: int = 30) -> dict:
        rid = self._next_id()
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = fut
        await self._ws.send(json.dumps({
            "jsonrpc": "2.0", "id": rid, "method": method, "params": params,
        }))
        try:
            resp = await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(rid, None)
            raise TimeoutError(f"{method} timeout")
        if "error" in resp:
            raise RuntimeError(resp["error"].get("message", str(resp["error"])))
        return resp.get("result", {})

    # -- ACP handshake --
    async def initialize(self) -> None:
        await self._request("initialize", {
            "protocolVersion": 1,
            "clientCapabilities": {"fs": {"readTextFile": True, "writeTextFile": True}},
        })
        await self._request("authenticate", {"methodId": "iflow"})

    # -- session --
    async def create_session(self, workspace: str, model: str = "claude-opus-4-6") -> str:
        result = await self._request("session/new", {
            "cwd": workspace,
            "mcpServers": [],
            "settings": {"permission_mode": "yolo", "model": model},
        })
        sid = result.get("sessionId", "")
        self.session_id = sid
        # 尝试设置模型
        try:
            await self._request("session/set_model", {
                "sessionId": sid, "modelId": model,
            }, timeout=10)
        except Exception:
            pass
        return sid

    async def load_session(self, session_id: str, workspace: str) -> bool:
        try:
            result = await self._request("session/load", {
                "sessionId": session_id,
                "cwd": workspace,
                "mcpServers": [],
            })
            if result.get("loaded", False):
                self.session_id = session_id
                return True
        except Exception:
            pass
        return False

    # -- prompt (streaming) --
    async def prompt_stream(self, message: str) -> str:
        """发送消息，流式打印回复，返回完整文本。"""
        if not self.session_id:
            raise RuntimeError("No active session")

        rid = self._next_id()
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = fut

        await self._ws.send(json.dumps({
            "jsonrpc": "2.0", "id": rid,
            "method": "session/prompt",
            "params": {
                "sessionId": self.session_id,
                "prompt": [{"type": "text", "text": message}],
            },
        }))

        content_parts: list[str] = []
        thought_parts: list[str] = []
        in_thought = False
        start = time.time()

        while True:
            if time.time() - start > self.timeout:
                self._pending.pop(rid, None)
                print("\n[超时]", file=sys.stderr)
                break

            if fut.done():
                # drain remaining notifications
                while not self._notification_queue.empty():
                    msg = self._notification_queue.get_nowait()
                    self._handle_update(msg, content_parts, thought_parts)
                break

            try:
                msg = await asyncio.wait_for(self._notification_queue.get(), timeout=1.0)
                self._handle_update(msg, content_parts, thought_parts)
            except asyncio.TimeoutError:
                continue

        # check final response for errors
        if fut.done():
            resp = fut.result()
            if "error" in resp:
                err = resp["error"].get("message", str(resp["error"]))
                print(f"\n[错误] {err}", file=sys.stderr)

        print()  # newline after streaming output
        return "".join(content_parts)

    def _handle_update(self, msg: dict, content_parts: list[str], thought_parts: list[str]) -> None:
        if msg.get("method") != "session/update":
            return
        update = msg.get("params", {}).get("update", {})
        utype = update.get("sessionUpdate", "")

        if utype == "agent_thought_chunk":
            content = update.get("content", {})
            if isinstance(content, dict) and content.get("type") == "text":
                text = content.get("text", "")
                if text:
                    if not thought_parts:
                        print("\033[2m", end="", flush=True)  # dim
                    thought_parts.append(text)
                    print(text, end="", flush=True)

        elif utype == "agent_message_chunk":
            content = update.get("content", {})
            if isinstance(content, dict) and content.get("type") == "text":
                text = content.get("text", "")
                if text:
                    if thought_parts and not content_parts:
                        print("\033[0m\n", end="", flush=True)  # reset dim
                    content_parts.append(text)
                    print(text, end="", flush=True)

        elif utype == "tool_call":
            name = update.get("name", "unknown")
            print(f"\n\033[33m[工具] {name}\033[0m", flush=True)

        elif utype == "tool_call_update":
            status = update.get("status", "")
            if status in ("completed", "failed"):
                name = update.get("name", "")
                color = "32" if status == "completed" else "31"
                print(f"\033[{color}m[工具 {status}] {name}\033[0m", flush=True)


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------
async def main(host: str, port: int, force_new: bool, workspace: str, model: str) -> None:
    client = TerminalACPClient(host=host, port=port)

    print(f"连接 ACP server ws://{host}:{port}/acp ...")
    try:
        await client.connect()
        await client.initialize()
    except Exception as e:
        print(f"连接失败: {e}", file=sys.stderr)
        return

    print("已连接。", end="")

    # 尝试复用已有 session
    if not force_new:
        existing_sid = load_session_id()
        if existing_sid:
            loaded = await client.load_session(existing_sid, workspace)
            if loaded:
                print(f" 已恢复会话 {existing_sid[:16]}...")
            else:
                print(f" 旧会话 {existing_sid[:16]}... 无法加载，创建新会话。")
                sid = await client.create_session(workspace, model)
                save_session_id(sid)
                print(f" 新会话 {sid[:16]}...")
        else:
            sid = await client.create_session(workspace, model)
            save_session_id(sid)
            print(f" 新会话 {sid[:16]}...")
    else:
        sid = await client.create_session(workspace, model)
        save_session_id(sid)
        print(f" 新会话 {sid[:16]}...")

    print("输入消息开始对话。/new 新建会话，/quit 退出。\n")

    try:
        while True:
            try:
                user_input = input("\033[1m主任 > \033[0m")
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            text = user_input.strip()
            if not text:
                continue

            if text == "/quit":
                print("再见！")
                break
            elif text == "/new":
                sid = await client.create_session(workspace, model)
                save_session_id(sid)
                print(f"已创建新会话 {sid[:16]}...")
                continue
            elif text == "/status":
                print(f"  ACP: ws://{host}:{port}/acp")
                print(f"  Session: {client.session_id or 'none'}")
                print(f"  Workspace: {workspace}")
                continue

            print(f"\033[36m妖妖酒 > \033[0m", end="", flush=True)
            await client.prompt_stream(text)

    finally:
        await client.disconnect()


def cli() -> None:
    parser = argparse.ArgumentParser(description="iFlow ACP 终端客户端")
    parser.add_argument("--host", default="localhost", help="ACP server host")
    parser.add_argument("--port", type=int, default=8090, help="ACP server port")
    parser.add_argument("--new", action="store_true", help="强制创建新会话")
    parser.add_argument("--workspace", default="/root/.iflow-bot/workspace", help="工作目录")
    parser.add_argument("--model", default="claude-opus-4-6", help="默认模型")
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port, args.new, args.workspace, args.model))


if __name__ == "__main__":
    cli()
