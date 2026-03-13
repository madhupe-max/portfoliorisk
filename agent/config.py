"""Configuration defaults for the portfolio risk LangGraph agent."""

from __future__ import annotations

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
DEFAULT_WEIGHTS = {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.20,
    "AMZN": 0.15,
    "TSLA": 0.15,
}
DEFAULT_RETURNS_METHOD = "simple"
DEFAULT_RISK_FREE_RATE = 0.02
ALLOWED_RETURNS_METHODS = {"simple", "log"}
