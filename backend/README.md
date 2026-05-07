# Arbitrage System (Backend)

This repository contains a FastAPI backend for a crypto arbitrage system.

What's included
- `api.py` - FastAPI application exposing:
  - `GET /opportunities` (REST) - returns latest 20 arbitrage opportunities (keeps previous API shape)
  - `WS /ws/opportunities` (WebSocket) - streams latest opportunities every 3 seconds
- `db.py` - async aiomysql pool helper
- `worker.py` - optional async worker to poll exchanges and store prices/arbitrage
- `main.py` - legacy synchronous polling script (kept for backward compatibility)

Setup

1. Create a Python 3.10+ virtual environment and activate it.

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Ensure your MySQL server is running and the credentials in `config.py` are correct.

Run API (development):

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Run worker (optional background process that writes to DB):

```bash
python3 worker.py
```

WebSocket usage (frontend):

Connect to `ws://<host>:8000/ws/opportunities` and you'll receive a JSON array of latest opportunities every 3 seconds.

Notes
- The repository now uses an async MySQL connection pool via `aiomysql`.
- `main.py` was left unchanged to avoid breaking existing workflows. Prefer `worker.py` for async operation.
