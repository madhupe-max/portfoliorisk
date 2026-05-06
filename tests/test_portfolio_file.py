"""Tests for flat-file portfolio loading utilities."""

from __future__ import annotations

import json

from portfolio_risk import load_portfolio_file


def test_load_json_portfolio_with_tickers_and_weights(tmp_path):
    portfolio_file = tmp_path / "portfolio.json"
    portfolio_file.write_text(
        json.dumps(
            {
                "tickers": ["aapl", "msft"],
                "weights": {"aapl": 0.6, "msft": 0.4},
            }
        ),
        encoding="utf-8",
    )

    payload = load_portfolio_file(portfolio_file)

    assert payload["tickers"] == ["AAPL", "MSFT"]
    assert payload["weights"] == {"AAPL": 0.6, "MSFT": 0.4}


def test_load_csv_portfolio(tmp_path):
    portfolio_file = tmp_path / "portfolio.csv"
    portfolio_file.write_text(
        "ticker,weight\nAAPL,0.7\nMSFT,0.3\n",
        encoding="utf-8",
    )

    payload = load_portfolio_file(portfolio_file)

    assert payload["tickers"] == ["AAPL", "MSFT"]
    assert payload["weights"] == {"AAPL": 0.7, "MSFT": 0.3}
