"""Async worker to fetch prices and broadcast arbitrage opportunities.

This worker polls Binance and Bybit every 2 seconds, computes the
arbitrage opportunity, stores it in the in-memory `db` and broadcasts
the same JSON payload to connected WebSocket clients via ws_manager.
"""
import asyncio
import logging
from typing import Optional

import httpx

from . import db
from .ws_manager import manager as ws_manager

logger = logging.getLogger("arbitrage.worker")


async def fetch_binance_price(client: httpx.AsyncClient) -> Optional[float]:
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    try:
        r = await client.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        return float(data.get("price"))
    except Exception:
        logger.exception("Failed fetching Binance price")
        return None


async def fetch_bybit_price(client: httpx.AsyncClient) -> Optional[float]:
    url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
    try:
        r = await client.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        return float(data.get("result", {}).get("list", [])[0].get("lastPrice"))
    except Exception:
        logger.exception("Failed fetching Bybit price")
        return None


async def process_iteration(client: httpx.AsyncClient) -> None:
    binance_price = await fetch_binance_price(client)
    bybit_price = await fetch_bybit_price(client)

    if binance_price is None or bybit_price is None:
        logger.debug("Skipping iteration due to missing prices")
        return

    spread = bybit_price - binance_price
    profit_percent = (spread / binance_price) * 100 if binance_price else None

    # Prepare payload following existing frontend shape
    payload = {
        "symbol": "BTCUSDT",
        "buy_exchange": "Binance",
        "sell_exchange": "Bybit",
        "buy_price": float(binance_price),
        "sell_price": float(bybit_price),
        "spread": float(spread),
        "profit_percent": float(profit_percent) if profit_percent is not None else None,
        # created_at will be added by db.add_opportunity if not provided
        "created_at": None,
    }

    # Store in-memory
    await db.add_opportunity(
        symbol=payload["symbol"],
        buy_exchange=payload["buy_exchange"],
        sell_exchange=payload["sell_exchange"],
        buy_price=payload["buy_price"],
        sell_price=payload["sell_price"],
        spread=payload["spread"],
        profit_percent=payload["profit_percent"],
    )

    # Broadcast latest single-item list to sockets (frontend expects array)
    try:
        await ws_manager.broadcast([payload])
    except Exception:
        logger.exception("Failed broadcasting payload to WS clients")


async def run_worker(poll_interval: float = 2.0) -> None:
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await process_iteration(client)
            except Exception:
                logger.exception("Unhandled error in worker loop")
            await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
