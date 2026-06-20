"""Tiny WebSocket broadcaster for live capture events."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


class WebSocketBroadcaster:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.clients: set[Any] = set()
        self._server: Any = None

    async def start(self) -> None:
        try:
            import websockets
        except ImportError as exc:
            raise RuntimeError("Missing dependency: pip install websockets") from exc

        async def handler(websocket: Any) -> None:
            self.clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.clients.discard(websocket)

        self._server = await websockets.serve(handler, self.host, self.port)

    async def broadcast(self, payload: str) -> None:
        if not self.clients:
            return
        stale = []
        for client in list(self.clients):
            try:
                await client.send(payload)
            except Exception:
                stale.append(client)
        for client in stale:
            self.clients.discard(client)

    async def stop(self) -> None:
        if self._server is None:
            return
        self._server.close()
        await self._server.wait_closed()


async def run_until_cancelled(fn: Callable[[], Awaitable[None]]) -> None:
    try:
        await fn()
    except asyncio.CancelledError:
        raise
