"""Tests for FastAPI HTTP wrapper around the portfolio risk agent."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "date" in payload


def test_analyze_endpoint_runs_agent(monkeypatch):
    expected = {
        "status": "completed",
        "as_of": "2026-03-13",
        "portfolio": {"tickers": ["AAPL"], "weights": {"AAPL": 1.0}, "summary": {}},
        "risk": {},
        "correlation": {},
        "narrative": "ok",
        "warnings": [],
        "errors": [],
    }

    def _fake_runner(payload):
        assert payload["tickers"] == ["AAPL"]
        assert payload["weights"] == {"AAPL": 1.0}
        return expected

    monkeypatch.setattr("api.app.run_portfolio_risk_agent", _fake_runner)

    response = client.post(
        "/analyze",
        json={
            "tickers": ["AAPL"],
            "weights": {"AAPL": 1.0},
            "returns_method": "simple",
            "risk_free_rate": 0.02,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected
