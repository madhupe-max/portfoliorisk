"""LangGraph workflow for portfolio risk analysis."""

from __future__ import annotations

from datetime import date
from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.config import (
    ALLOWED_RETURNS_METHODS,
    DEFAULT_RETURNS_METHOD,
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_TICKERS,
    DEFAULT_WEIGHTS,
)
from agent.prompts import build_risk_narrative
from agent.state import AgentError, PortfolioRiskAgentState
from agent.tools import build_portfolio, calculate_correlation_summary, calculate_risk_summary, load_market_data


def _agent_error(error_code: str, message: str, recoverable: bool = False, details: dict[str, Any] | None = None) -> AgentError:
    return {
        "error_code": error_code,
        "message": message,
        "recoverable": recoverable,
        "details": details or {},
    }


def resolve_input_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    payload = state.get("input_portfolio", {})
    tickers = payload.get("tickers") or DEFAULT_TICKERS
    weights = payload.get("weights") or DEFAULT_WEIGHTS

    return {
        **state,
        "tickers": tickers,
        "weights": weights,
        "start_date": payload.get("start_date"),
        "end_date": payload.get("end_date"),
        "returns_method": payload.get("returns_method", DEFAULT_RETURNS_METHOD),
        "risk_free_rate": float(payload.get("risk_free_rate", DEFAULT_RISK_FREE_RATE)),
        "warnings": state.get("warnings", []),
        "errors": state.get("errors", []),
        "status": "running",
        "as_of": date.today().isoformat(),
    }


def validate_input_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    tickers = state.get("tickers", [])
    weights = state.get("weights", {})
    method = state.get("returns_method", DEFAULT_RETURNS_METHOD)

    errors = list(state.get("errors", []))

    if not tickers:
        errors.append(_agent_error("INVALID_TICKERS", "Tickers list cannot be empty."))

    if not weights:
        errors.append(_agent_error("INVALID_WEIGHTS", "Weights map cannot be empty."))

    weight_keys = set(weights.keys())
    ticker_keys = set(tickers)
    if weight_keys != ticker_keys:
        errors.append(
            _agent_error(
                "TICKER_WEIGHT_MISMATCH",
                "Weights keys must exactly match ticker list.",
                details={"tickers": tickers, "weight_keys": sorted(list(weight_keys))},
            )
        )

    weight_sum = float(sum(weights.values())) if weights else 0.0
    if abs(weight_sum - 1.0) > 1e-8:
        errors.append(
            _agent_error(
                "WEIGHT_SUM_INVALID",
                "Portfolio weights must sum to 1.0.",
                details={"weight_sum": weight_sum},
            )
        )

    if method not in ALLOWED_RETURNS_METHODS:
        errors.append(
            _agent_error(
                "INVALID_RETURNS_METHOD",
                "returns_method must be 'simple' or 'log'.",
                details={"returns_method": method},
            )
        )

    return {**state, "errors": errors}


def load_market_data_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    try:
        prices, returns = load_market_data(
            tickers=state["tickers"],
            start_date=state.get("start_date"),
            end_date=state.get("end_date"),
            returns_method=state.get("returns_method", DEFAULT_RETURNS_METHOD),
        )
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "MARKET_DATA_FETCH_FAILED",
            str(exc),
            recoverable=False,
            details={"tickers": state["tickers"]},
        ))
        return {**state, "errors": errors}

    if returns.empty:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "EMPTY_RETURNS",
            "No returns data available after processing prices.",
            recoverable=False,
            details={"tickers": state["tickers"]},
        ))
        return {**state, "errors": errors}

    return {**state, "prices": prices, "returns": returns}


def build_portfolio_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    try:
        portfolio, summary = build_portfolio(state["weights"], state["returns"])
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "PORTFOLIO_BUILD_FAILED",
            str(exc),
            recoverable=False,
            details={"tickers": state["tickers"]},
        ))
        return {**state, "errors": errors}
    return {**state, "portfolio_obj": portfolio, "portfolio_summary": summary}


def compute_risk_metrics_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    try:
        risk_summary = calculate_risk_summary(state["portfolio_obj"], state["risk_free_rate"])
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "RISK_METRICS_FAILED",
            str(exc),
            recoverable=False,
        ))
        return {**state, "errors": errors}
    return {**state, "risk_summary": risk_summary}


def compute_correlation_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    try:
        correlation_summary = calculate_correlation_summary(
            returns_data=state["returns"],
            weights=state["weights"],
            reference_ticker=state["tickers"][0],
        )
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "CORRELATION_FAILED",
            str(exc),
            recoverable=False,
            details={"reference_ticker": state["tickers"][0]},
        ))
        return {**state, "errors": errors}
    return {**state, "correlation_summary": correlation_summary}


def generate_report_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    try:
        narrative = build_risk_narrative(state["risk_summary"], state["correlation_summary"])
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(_agent_error(
            "REPORT_GENERATION_FAILED",
            str(exc),
            recoverable=False,
        ))
        return {**state, "errors": errors}
    return {**state, "narrative": narrative}


def finalize_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    return {
        **state,
        "status": "completed" if not state.get("errors") else "failed",
        "portfolio": {
            "tickers": state.get("tickers", []),
            "weights": state.get("weights", {}),
            "summary": state.get("portfolio_summary", {}),
        },
        "risk": state.get("risk_summary", {}),
        "correlation": state.get("correlation_summary", {}),
    }


def error_node(state: PortfolioRiskAgentState) -> PortfolioRiskAgentState:
    return {**state, "status": "failed"}


def _route_on_errors(state: PortfolioRiskAgentState) -> str:
    return "error" if state.get("errors") else "ok"


def build_graph():
    graph = StateGraph(PortfolioRiskAgentState)

    graph.add_node("resolve_input", resolve_input_node)
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("load_market_data", load_market_data_node)
    graph.add_node("build_portfolio", build_portfolio_node)
    graph.add_node("compute_risk_metrics", compute_risk_metrics_node)
    graph.add_node("compute_correlation", compute_correlation_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("finalize", finalize_node)
    graph.add_node("error", error_node)

    graph.add_edge(START, "resolve_input")
    graph.add_edge("resolve_input", "validate_input")
    graph.add_conditional_edges(
        "validate_input",
        _route_on_errors,
        {
            "ok": "load_market_data",
            "error": "error",
        },
    )
    graph.add_conditional_edges("load_market_data", _route_on_errors, {"ok": "build_portfolio", "error": "error"})
    graph.add_conditional_edges("build_portfolio", _route_on_errors, {"ok": "compute_risk_metrics", "error": "error"})
    graph.add_conditional_edges("compute_risk_metrics", _route_on_errors, {"ok": "compute_correlation", "error": "error"})
    graph.add_conditional_edges("compute_correlation", _route_on_errors, {"ok": "generate_report", "error": "error"})
    graph.add_conditional_edges("generate_report", _route_on_errors, {"ok": "finalize", "error": "error"})
    graph.add_edge("finalize", END)
    graph.add_edge("error", END)

    return graph.compile()


def _safe_for_json(value: Any):
    """Best-effort conversion for pandas/numpy values in outputs."""
    try:
        import numpy as np
        import pandas as pd

        if isinstance(value, pd.DataFrame):
            return value.to_dict()
        if isinstance(value, pd.Series):
            return value.to_dict()
        if isinstance(value, (np.floating, np.integer)):
            return value.item()
    except Exception:
        pass

    if isinstance(value, dict):
        return {k: _safe_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe_for_json(v) for v in value]
    return value


def run_portfolio_risk_agent(input_portfolio: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute the portfolio risk graph and return a JSON-serializable result."""
    graph = build_graph()
    initial_state: PortfolioRiskAgentState = {
        "input_portfolio": input_portfolio or {},
        "warnings": [],
        "errors": [],
        "status": "initialized",
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as exc:
        return {
            "status": "failed",
            "errors": [
                _agent_error(
                    "UNHANDLED_EXCEPTION",
                    str(exc),
                    recoverable=False,
                )
            ],
            "warnings": [],
            "portfolio": {},
            "risk": {},
            "correlation": {},
            "narrative": "",
            "as_of": date.today().isoformat(),
        }

    response = {
        "status": result.get("status", "failed"),
        "as_of": result.get("as_of", date.today().isoformat()),
        "portfolio": result.get("portfolio", {}),
        "risk": result.get("risk", {}),
        "correlation": result.get("correlation", {}),
        "narrative": result.get("narrative", ""),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
    }

    return _safe_for_json(response)
