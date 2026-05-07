"""Async worker to fetch prices and store arbitrage opportunities.

This is a non-blocking replacement for the existing `main.py` polling
script. It uses `httpx` for async HTTP requests and the async DB pool
provided in `db.py`.
"""
import asyncio
import logging
from typing import Tuple

import httpx

import db
import config

logger = logging.getLogger("arbitrage.worker")


async def fetch_binance_price(client: httpx.AsyncClient) -> float:
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = await client.get(url, timeout=10.0)
    r.raise_for_status()
    data = r.json()
    return float(data["price"])


async def fetch_bybit_price(client: httpx.AsyncClient) -> float:
    url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
    r = await client.get(url, timeout=10.0)
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["list"][0]["lastPrice"])


async def store_prices_and_arb(binance_price: float, bybit_price: float):
    spread = bybit_price - binance_price
    profit_percent = (spread / binance_price) * 100

    # Use a new connection so worker doesn't rely on API startup pool.
    # Reuse the global pool for efficiency.
    sql_price = """
    INSERT INTO prices (exchange_name, symbol, price)
    VALUES (%s, %s, %s)
    """

    sql_arb = """
    INSERT INTO arbitrage_opportunities
    (buy_exchange, sell_exchange, symbol, buy_price, sell_price, spread, profit_percent)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Acquire a connection from the pool and execute statements
    global db
    pool = db._pool  # type: ignore
    if pool is None:
        raise RuntimeError("DB pool not initialized in worker")

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_price, ("Binance", "BTCUSDT", binance_price))
            await cur.execute(sql_price, ("Bybit", "BTCUSDT", bybit_price))
            await cur.execute(sql_arb, ("Binance", "Bybit", "BTCUSDT", binance_price, bybit_price, spread, profit_percent))
            await conn.commit()


async def run_worker(poll_interval: float = 5.0):
    # Initialize DB pool for worker
    await db.init_pool(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)

    async with httpx.AsyncClient() as client:
        try:
            while True:
                try:
                    binance_price = await fetch_binance_price(client)
                    bybit_price = await fetch_bybit_price(client)

                    logger.info("Binance: %s Bybit: %s", binance_price, bybit_price)

                    await store_prices_and_arb(binance_price, bybit_price)
                    logger.info("Stored prices and arbitrage opportunity")
                except Exception:
                    logger.exception("Error during worker iteration")

                await asyncio.sleep(poll_interval)
        finally:
            await db.close_pool()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
