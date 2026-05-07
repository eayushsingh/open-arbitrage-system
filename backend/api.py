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

logger = logging.getLogger("arbitrage.api")

app = FastAPI(title="Arbitrage System API")

# Allow browser-based clients from any origin in development. For
# production, lock this down to the frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize DB connection pool on startup."""
    logger.info("Starting up: initializing DB pool")
    await db.init_pool(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        minsize=1,
        maxsize=10,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Close DB pool on shutdown."""
    logger.info("Shutting down: closing DB pool")
    await db.close_pool()


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
    # Accept the websocket connection and log client info if available
    await websocket.accept()
    client = websocket.client
    if client:
        logger.info("WebSocket client connected: %s:%s", client.host, client.port)
    else:
        logger.info("WebSocket client connected: /ws/opportunities")

    try:
        while True:
            # Fetch latest opportunities from the async pool. db.fetch_opportunities
            # returns a list of normalized dicts (possibly empty).
            opportunities = await db.fetch_opportunities(limit=20)

            # Ensure the payload is always a JSON array (even if empty)
            payload = opportunities if isinstance(opportunities, list) else [opportunities]

            # Send JSON payload. Wrap in try/except so transient serialization
            # issues don't crash the websocket loop.
            try:
                await websocket.send_json(payload)
            except Exception:
                logger.exception("Failed sending WS payload to client; continuing")

            # Sleep in a non-blocking way so other requests are served.
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        client = websocket.client
        if client:
            logger.info("WebSocket client disconnected: %s:%s", client.host, client.port)
        else:
            logger.info("WebSocket client disconnected: /ws/opportunities")
    except Exception as exc:  # pylint: disable=broad-except
        # On unexpected errors, log and close the connection gracefully.
        logger.exception("Error in WebSocket loop: %s", exc)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass