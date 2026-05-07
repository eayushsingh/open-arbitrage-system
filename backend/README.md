# Arbitrage System (Backend)

This repository contains a FastAPI backend for a crypto arbitrage system.

What's included
- `api.py` - FastAPI application exposing:
  - `GET /opportunities` (REST) - returns latest 20 arbitrage opportunities (keeps previous API shape)
  - `WS /ws/opportunities` (WebSocket) - streams latest opportunities every 3 seconds
- `db.py` - in-memory storage for opportunities (no external DB required)
- `worker.py` - async worker to poll exchanges and broadcast opportunities
- `main.py` - legacy synchronous polling script (kept for backward compatibility)

Setup

1. Create a Python 3.10+ virtual environment and activate it.

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run API (development):

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Run worker (background poller that stores in-memory and broadcasts):

```bash
python3 worker.py
```

WebSocket usage (frontend):

In production the deployed backend is available at:

```
https://open-arbitrage-system.onrender.com
```

For WebSocket connections, use the `wss` URL in production:

```
wss://open-arbitrage-system.onrender.com/ws/opportunities
```

Notes
- The backend now uses an in-memory store for opportunities and does not require an external database. This makes it suitable for deployment to platforms like Render without a managed database.
- `main.py` is legacy and kept for reference. Use `worker.py` for the async polling/broadcasting loop.
