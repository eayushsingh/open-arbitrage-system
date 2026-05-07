"""Configuration for the arbitrage system.

Defaults mirror the previous hard-coded values. These can be overridden
via environment variables in production deployments.
"""
import os

# Frontend origins allowed for CORS. Set to your deployed frontend URL(s)
# e.g. https://your-frontend.vercel.app or http://localhost:5173 for dev.
# Comma-separated list supported via FRONTEND_ORIGINS env var.
_origins = os.getenv("FRONTEND_ORIGINS", "*")
# Allow wildcard '*' to represent any origin, otherwise split by commas
if _origins.strip() == "*":
	FRONTEND_ORIGINS = ["*"]
else:
	FRONTEND_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]

# Note: DB is now in-memory. Previous DB_* environment variables removed.
