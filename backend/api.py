from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

opportunities = []

@app.get("/")
async def root():
    return {"message": "Backend running"}

@app.get("/opportunities")
async def get_opportunities():
    return opportunities[-20:]

@app.websocket("/ws/opportunities")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = {
            "symbol": "BTCUSDT",
            "buy_exchange": "Binance",
            "sell_exchange": "Bybit",
            "buy_price": round(random.uniform(79000, 80000), 2),
            "sell_price": round(random.uniform(80000, 81000), 2),
            "spread": round(random.uniform(1, 15), 2),
            "profit_percent": round(random.uniform(0.001, 0.02), 4),
            "created_at": str(datetime.now())
        }

        opportunities.append(data)

        await websocket.send_json(data)

        await asyncio.sleep(2)
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

opportunities = []

@app.get("/")
async def root():
    return {"message": "Backend running"}

@app.get("/opportunities")
async def get_opportunities():
    return opportunities[-20:]

@app.websocket("/ws/opportunities")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = {
            "symbol": "BTCUSDT",
            "buy_exchange": "Binance",
            "sell_exchange": "Bybit",
            "buy_price": round(random.uniform(79000, 80000), 2),
            "sell_price": round(random.uniform(80000, 81000), 2),
            "spread": round(random.uniform(1, 15), 2),
            "profit_percent": round(random.uniform(0.001, 0.02), 4),
            "created_at": str(datetime.now())
        }

        opportunities.append(data)

        await websocket.send_json(data)

        await asyncio.sleep(2)