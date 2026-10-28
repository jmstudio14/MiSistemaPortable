from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from core.paths import DESKTOP_COMMANDER_ENTRY, MCP_DATA_DIR, NODE_EXE, ensure_writable_dirs


class DesktopCommanderManager:
    """Starts Desktop Commander as a private child process; no global Node install needed."""

    def _prepare(self) -> None:
        ensure_writable_dirs()
        if not NODE_EXE.is_file() or not DESKTOP_COMMANDER_ENTRY.is_file():
            raise FileNotFoundError(
                "El runtime de Desktop Commander no está dentro del paquete. Ejecuta build_portable.bat para generarlo."
            )
        config_file = MCP_DATA_DIR / "config.json"
        if not config_file.exists():
            config_file.write_text(
                json.dumps({"telemetryEnabled": False}, indent=2), encoding="utf-8"
            )

    async def _list_tools_async(self) -> list[dict[str, str]]:
        self._prepare()
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        env = dict(os.environ)
        env["NO_COLOR"] = "1"
        params = StdioServerParameters(
            command=str(NODE_EXE),
            args=[str(DESKTOP_COMMANDER_ENTRY), "--no-onboarding"],
            env=env,
            cwd=str(MCP_DATA_DIR),
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                return [
                    {"name": tool.name, "description": (tool.description or "")[:180]}
                    for tool in response.tools
                ]

    def list_tools(self) -> list[dict[str, str]]:
        return asyncio.run(self._list_tools_async())

    async def _call_tool_async(self, name: str, arguments: dict[str, Any]) -> str:
        self._prepare()
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        env = dict(os.environ)
        env["NO_COLOR"] = "1"
        params = StdioServerParameters(
            command=str(NODE_EXE),
            args=[str(DESKTOP_COMMANDER_ENTRY), "--no-onboarding"],
            env=env,
            cwd=str(MCP_DATA_DIR),
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.call_tool(name, arguments)
                chunks = []
                for block in getattr(response, "content", []):
                    if getattr(block, "text", None):
                        chunks.append(block.text)
                return "\n".join(chunks) if chunks else str(response)[:4000]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        # Deliberately not called directly by the SLM. A UI confirmation gate must be added
        # before exposing calls that can edit files, launch processes, or run terminal commands.
        return asyncio.run(self._call_tool_async(name, arguments))
