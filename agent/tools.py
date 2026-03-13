"""Tool wrappers that bridge the agent to portfolio_risk domain modules."""

from __future__ import annotations

from portfolio_risk import CorrelationAnalyzer, DataLoader, Portfolio, RiskMetrics


def load_market_data(tickers: list[str], start_date: str | None, end_date: str | None, returns_method: str):
    """Fetch prices and compute returns for tickers."""
    loader = DataLoader(start_date=start_date, end_date=end_date)
    prices = loader.fetch_data(tickers)
    returns = loader.get_returns(prices, method=returns_method)
    return prices, returns


def build_portfolio(weights: dict[str, float], returns_data):
    """Create a Portfolio instance and return it with summary data."""
    portfolio = Portfolio(weights, returns_data)
    return portfolio, portfolio.get_summary()


def calculate_risk_summary(portfolio: Portfolio, risk_free_rate: float):
    """Calculate risk summary, honoring caller-provided risk-free rate."""
    returns = portfolio.get_portfolio_returns()
    summary = RiskMetrics.get_risk_summary(portfolio)
    summary["Sharpe Ratio"] = RiskMetrics.sharpe_ratio(portfolio, risk_free_rate=risk_free_rate)
    summary["Sortino Ratio"] = RiskMetrics.sortino_ratio(returns, risk_free_rate=risk_free_rate)
    return summary


def calculate_correlation_summary(returns_data, weights: dict[str, float], reference_ticker: str):
    """Calculate correlation and concentration metrics."""
    analyzer = CorrelationAnalyzer(returns_data)
    diversifiers = analyzer.find_diversifiers(reference_ticker, num_results=3).to_dict()
    concentration = analyzer.get_concentration_report(portfolio_weights_to_series(weights))
    return {
        "average_correlation": analyzer.get_average_correlation(),
        "diversifiers": diversifiers,
        "concentration": concentration,
    }


def portfolio_weights_to_series(weights: dict[str, float]):
    """Convert weight dict to pandas Series lazily to avoid hard dependency in helper signatures."""
    import pandas as pd

    return pd.Series(weights)
