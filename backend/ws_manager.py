"""Simple WebSocket manager to track connected clients and broadcast.

Keeps a set of connected WebSocket objects and provides async broadcast
that catches and removes disconnected clients.
"""
from typing import Any, Set
import asyncio
import logging

from fastapi import WebSocket

logger = logging.getLogger("arbitrage.ws_manager")


class WSManager:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.add(ws)
        logger.info("WS client connected (total=%d)", len(self._clients))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            if ws in self._clients:
                self._clients.remove(ws)
        logger.info("WS client disconnected (total=%d)", len(self._clients))

    async def broadcast(self, message: Any) -> None:
        """Send JSON-serializable `message` to all connected clients.

        Removes clients that raise during send.
        """
        async with self._lock:
            clients = list(self._clients)

        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                logger.exception("Error sending WS message; removing client")
                try:
                    await self.disconnect(ws)
                except Exception:
                    pass


# Module-level manager instance for easy import/use
manager = WSManager()
