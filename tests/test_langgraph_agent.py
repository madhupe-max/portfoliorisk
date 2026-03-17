"""Integration-style tests for the LangGraph portfolio risk agent."""

from __future__ import annotations

import pytest
import pandas as pd

langgraph = pytest.importorskip("langgraph")

from agent.portfolio_risk_agent import run_portfolio_risk_agent


@pytest.fixture
def mock_market_data(monkeypatch):
    """Mock market data loading to avoid network calls."""
    dates = pd.date_range("2024-01-01", periods=6, freq="D")
    prices = pd.DataFrame(
        {
            "AAPL": [100, 101, 102, 103, 104, 105],
            "MSFT": [200, 201, 203, 204, 205, 206],
            "GOOGL": [150, 149, 151, 152, 154, 155],
            "AMZN": [120, 121, 122, 121, 123, 124],
            "TSLA": [90, 92, 91, 93, 94, 95],
        },
        index=dates,
    )

    def _fetch_data(self, tickers):
        return prices[tickers]

    def _get_returns(self, price_df, method="simple"):
        return price_df.pct_change().dropna()

    monkeypatch.setattr("portfolio_risk.data_loader.DataLoader.fetch_data", _fetch_data)
    monkeypatch.setattr("portfolio_risk.data_loader.DataLoader.get_returns", _get_returns)


def test_agent_default_portfolio_success(mock_market_data):
    result = run_portfolio_risk_agent()

    assert result["status"] == "completed"
    assert "portfolio" in result
    assert "risk" in result
    assert "correlation" in result
    assert isinstance(result["narrative"], str)
    assert result["portfolio"]["summary"]["Number of Assets"] == 5


def test_agent_invalid_weights_fails():
    payload = {
        "tickers": ["AAPL", "MSFT"],
        "weights": {"AAPL": 0.7, "MSFT": 0.4},
    }

    result = run_portfolio_risk_agent(payload)

    assert result["status"] == "failed"
    assert result["errors"]
    assert any(err["error_code"] == "WEIGHT_SUM_INVALID" for err in result["errors"])


def test_agent_market_data_fetch_failure_returns_structured_error(monkeypatch):
    """Verify computation-node exceptions produce structured AgentError, not UNHANDLED_EXCEPTION."""
    def _raise_fetch(self, tickers):
        raise RuntimeError("simulated network failure")

    monkeypatch.setattr("portfolio_risk.data_loader.DataLoader.fetch_data", _raise_fetch)

    payload = {
        "tickers": ["AAPL", "MSFT"],
        "weights": {"AAPL": 0.5, "MSFT": 0.5},
    }
    result = run_portfolio_risk_agent(payload)

    assert result["status"] == "failed"
    assert result["errors"], "Expected at least one error entry"
    error = result["errors"][0]
    assert error["error_code"] == "MARKET_DATA_FETCH_FAILED"
    assert "simulated network failure" in error["message"]
    assert error["details"]["tickers"] == ["AAPL", "MSFT"]
