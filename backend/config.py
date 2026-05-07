"""Configuration for the arbitrage system.

Defaults mirror the previous hard-coded values. These can be overridden
via environment variables in production deployments.
"""
import os

# Database defaults (same as previous code)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ayush123")
DB_NAME = os.getenv("DB_NAME", "arbitrage_system")
