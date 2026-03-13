"""Typed state definitions for the LangGraph portfolio risk agent."""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class AgentError(TypedDict, total=False):
    """Structured error payload."""

    error_code: str
    message: str
    recoverable: bool
    details: dict[str, Any]


class PortfolioRiskAgentState(TypedDict, total=False):
    """State passed between graph nodes."""

    input_portfolio: dict[str, Any]
    tickers: list[str]
    weights: dict[str, float]
    start_date: Optional[str]
    end_date: Optional[str]
    returns_method: str
    risk_free_rate: float
    prices: Any
    returns: Any
    portfolio_obj: Any
    portfolio_summary: dict[str, Any]
    risk_summary: dict[str, Any]
    correlation_summary: dict[str, Any]
    portfolio: dict[str, Any]
    risk: dict[str, Any]
    correlation: dict[str, Any]
    narrative: str
    warnings: list[str]
    errors: list[AgentError]
    status: str
    as_of: str
