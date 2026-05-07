"""Async database helpers using aiomysql connection pool.

This module provides a simple wrapper around an aiomysql pool to perform
non-blocking queries. It exposes init_pool/close_pool and a convenience
method fetch_opportunities used by the API.
"""

from typing import Any, Dict, List, Optional
import aiomysql
import logging

logger = logging.getLogger("arbitrage.db")

_pool: Optional[aiomysql.Pool] = None


async def init_pool(*, host: str, port: int, user: str, password: str, database: str, minsize: int = 1, maxsize: int = 10) -> None:
    """Initialize a global aiomysql pool.

    Args mirror connection parameters used by mysql.connector in the old code.
    """
    global _pool
    if _pool is not None:
        return

    logger.info("Initializing aiomysql pool to %s:%s/%s", host, port, database)
    _pool = await aiomysql.create_pool(host=host, port=port, user=user, password=password, db=database, minsize=minsize, maxsize=maxsize)


async def close_pool() -> None:
    """Close the global pool if initialized."""
    global _pool
    if _pool is None:
        return
    _pool.close()
    await _pool.wait_closed()
    _pool = None


async def fetch_opportunities(limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch latest arbitrage opportunities asynchronously.

    Returns list of dict rows (column names as keys).
    """
    global _pool
    # If pool not initialized yet, return empty list instead of raising.
    # This prevents WebSocket endpoints from crashing while the app is
    # starting or when worker hasn't inserted data yet.
    if _pool is None:
        logger.debug("DB pool uninitialized: returning empty opportunities list")
        return []

    sql = """
    SELECT * FROM arbitrage_opportunities
    ORDER BY created_at DESC
    LIMIT %s
    """

    try:
        async with _pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql, (limit,))
                rows = await cur.fetchall()
                # aiomysql returns dict-like rows with DictCursor
                result: List[Dict[str, Any]] = []
                for row in rows:
                    # Normalize and ensure JSON serializable types
                    r = dict(row)

                    # Map DB fields to required payload fields. Use .get with
                    # fallbacks to tolerate different DB column names.
                    symbol = r.get("symbol") or r.get("pair") or r.get("ticker") or "N/A"
                    buy_exchange = r.get("buy_exchange") or r.get("buyExchange") or r.get("buy") or ""
                    sell_exchange = r.get("sell_exchange") or r.get("sellExchange") or r.get("sell") or ""

                    # Price fields may be Decimal or string; coerce to float where possible
                    def _as_float(v):
                        try:
                            if v is None:
                                return None
                            return float(v)
                        except Exception:
                            return None

                    buy_price = _as_float(r.get("buy_price") or r.get("buyPrice") or r.get("buy"))
                    sell_price = _as_float(r.get("sell_price") or r.get("sellPrice") or r.get("sell"))
                    spread = _as_float(r.get("spread"))
                    profit_percent = _as_float(r.get("profit_percent") or r.get("profitPercent") or r.get("profit"))

                    created_at_val = r.get("created_at") or r.get("time") or r.get("timestamp")
                    # created_at may be datetime; convert to ISO string; fallback to current time
                    try:
                        if created_at_val is None:
                            created_at = None
                        else:
                            # If it's a datetime object, isoformat; if numeric, interpret as ms since epoch
                            import datetime

                            if isinstance(created_at_val, datetime.datetime):
                                created_at = created_at_val.isoformat()
                            else:
                                # attempt to coerce to float then to ISO
                                try:
                                    ts = float(created_at_val)
                                    # If timestamp looks like seconds, convert to ms
                                    if ts > 1e12:
                                        # already ms
                                        created_at = datetime.datetime.fromtimestamp(ts / 1000.0).isoformat()
                                    elif ts > 1e9:
                                        # seconds
                                        created_at = datetime.datetime.fromtimestamp(ts).isoformat()
                                    else:
                                        created_at = str(created_at_val)
                                except Exception:
                                    created_at = str(created_at_val)
                    except Exception:
                        created_at = None

                    payload = {
                        "symbol": symbol,
                        "buy_exchange": buy_exchange,
                        "sell_exchange": sell_exchange,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "spread": spread,
                        "profit_percent": profit_percent,
                        # created_at as ISO string or None
                        "created_at": created_at,
                    }
                    result.append(payload)

                return result
    except Exception:
        logger.exception("Error fetching opportunities from DB")
        return []
