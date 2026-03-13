"""FastAPI application exposing the portfolio risk agent over HTTP."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent import run_portfolio_risk_agent


class AnalyzeRequest(BaseModel):
    """Request payload for portfolio risk analysis."""

    tickers: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    returns_method: Optional[str] = Field(default=None, pattern="^(simple|log)$")
    risk_free_rate: Optional[float] = None


class AnalyzeResponse(BaseModel):
    """Response payload for portfolio risk analysis."""

    status: str
    as_of: str
    portfolio: Dict[str, Any]
    risk: Dict[str, Any]
    correlation: Dict[str, Any]
    narrative: str
    warnings: List[Any]
    errors: List[Any]


app = FastAPI(
    title="Portfolio Risk Agent API",
    version="0.1.0",
    description="HTTP interface for running LangGraph portfolio risk analysis.",
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Liveness endpoint."""
    return {"status": "ok", "date": date.today().isoformat()}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_portfolio(request: AnalyzeRequest) -> Dict[str, Any]:
    """Run the portfolio risk agent for the supplied payload."""
    payload = request.model_dump(exclude_none=True)
    return run_portfolio_risk_agent(payload)
