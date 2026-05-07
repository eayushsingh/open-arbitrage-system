"""In-memory storage for arbitrage opportunities.

This module replaces the previous aiomysql-backed implementation with a
simple thread-safe in-memory list. It exposes the same async-compatible
functions used by the API: fetch_opportunities(limit) and a new
add_opportunity(...) helper for the worker.

The stored dicts follow the JSON shape expected by the frontend:
  {
    "symbol": "BTCUSDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Bybit",
    "buy_price": 60000.0,
    "sell_price": 60100.0,
    "spread": 100.0,
    "profit_percent": 0.1667,
    "created_at": "2026-05-07T12:34:56.789Z"
  }

This module is intentionally small and synchronous behind the scenes but
provides async functions so callers don't need to change.
"""

from typing import Any, Dict, List, Optional
import asyncio
import datetime

# Internal storage and lock to make writes safe across async tasks
_OPPORTUNITIES: List[Dict[str, Any]] = []
_LOCK = asyncio.Lock()


async def fetch_opportunities(limit: int = 20) -> List[Dict[str, Any]]:
    """Return the most recent opportunities up to `limit`.

    Returns a shallow copy of the most recent items (newest first).
    """
    # No heavy work; just snapshot under the lock to avoid races with writer
    async with _LOCK:
        # Newest first: store with newest appended at front or slice accordingly
        snapshot = list(_OPPORTUNITIES[:limit])
    return snapshot


async def add_opportunity(
    symbol: str,
    buy_exchange: str,
    sell_exchange: str,
    buy_price: Optional[float],
    sell_price: Optional[float],
    spread: Optional[float],
    profit_percent: Optional[float],
    created_at: Optional[str] = None,
) -> None:
    """Add a new opportunity to in-memory storage.

    Keeps list capped at a reasonable size (default 500 entries).
    """
    if created_at is None:
        created_at = datetime.datetime.utcnow().isoformat() + "Z"

    payload: Dict[str, Any] = {
        "symbol": symbol,
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,
        "buy_price": float(buy_price) if buy_price is not None else None,
        "sell_price": float(sell_price) if sell_price is not None else None,
        "spread": float(spread) if spread is not None else None,
        "profit_percent": float(profit_percent) if profit_percent is not None else None,
        "created_at": created_at,
    }

    async with _LOCK:
        # Prepend to keep newest first
        _OPPORTUNITIES.insert(0, payload)
        # Cap list to 500 entries to bound memory
        if len(_OPPORTUNITIES) > 500:
            del _OPPORTUNITIES[500:]


# Backwards-compatible no-op functions for init/close to avoid changing imports
async def init_pool(*args, **kwargs) -> None:  # pragma: no cover - trivial
    return None


async def close_pool() -> None:  # pragma: no cover - trivial
    return None

