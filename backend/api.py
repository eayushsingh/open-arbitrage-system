"""API module for the arbitrage system.

This module exposes the FastAPI `app` instance and provides both a REST
endpoint and a WebSocket endpoint for arbitrage opportunities. The REST
endpoint `/opportunities` is kept compatible with the previous
implementation but is now async and uses a connection pool. The WebSocket
endpoint `/ws/opportunities` streams the latest opportunities every 3
seconds.
"""

import asyncio
import logging
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import db
import config
from ws_manager import manager as ws_manager

logger = logging.getLogger("arbitrage.api")

app = FastAPI(title="Arbitrage System API")

# Configure CORS using FRONTEND_ORIGINS from config. This allows locking
# to the deployed frontend origin(s) while defaulting to '*' for dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """No external DB to initialize; worker and in-memory store will be used."""
    logger.info("Starting up: in-memory store active")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown event: nothing to close for in-memory store")


@app.get("/opportunities")
async def get_opportunities():
    """Return the latest arbitrage opportunities (keeps previous API shape).

    Uses the async DB pool for non-blocking reads.
    """
    data = await db.fetch_opportunities(limit=20)
    return data


@app.websocket("/ws/opportunities")
async def websocket_opportunities(websocket: WebSocket):
    """WebSocket endpoint that streams latest opportunities every 3 seconds.

    The connection stays open until the client disconnects. Each tick
    queries the DB pool asynchronously and sends a JSON payload containing
    the latest rows.
    """
    # Accept the websocket and register with the manager. The manager will
    # handle broadcasting; this endpoint returns immediately and keeps the
    # connection open until disconnect.
    await websocket.accept()
    await ws_manager.connect(websocket)
    client = websocket.client
    if client:
        logger.info("WebSocket client connected: %s:%s", client.host, client.port)
    else:
        logger.info("WebSocket client connected: /ws/opportunities")

    try:
        # Keep the connection open and await client pings/messages to detect
        # disconnects. We don't expect incoming messages, but receiving them
        # prevents the websocket from being GC'd or timing out in some
        # environments.
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                raise
            except Exception:
                # Ignore non-disconnect exceptions; just yield to event loop.
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
        client = websocket.client
        if client:
            logger.info("WebSocket client disconnected: %s:%s", client.host, client.port)
        else:
            logger.info("WebSocket client disconnected: /ws/opportunities")
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error in WebSocket connection handler: %s", exc)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass