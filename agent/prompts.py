"""Narrative generation logic for portfolio risk analysis outputs."""

from __future__ import annotations


def build_risk_narrative(risk_summary: dict, correlation_summary: dict) -> str:
    """Create concise human-readable commentary from computed metrics."""
    sharpe = float(risk_summary.get("Sharpe Ratio", 0.0))
    max_drawdown = float(risk_summary.get("Maximum Drawdown", 0.0))
    top3 = float(correlation_summary.get("concentration", {}).get("Top 3 Concentration", 0.0))
    avg_corr = float(correlation_summary.get("average_correlation", 0.0))

    findings: list[str] = []

    if sharpe < 0.5:
        findings.append("Risk-adjusted return is weak (Sharpe Ratio below 0.5).")
    elif sharpe < 1.0:
        findings.append("Risk-adjusted return is moderate but could be improved.")
    else:
        findings.append("Risk-adjusted return is healthy for the observed period.")

    if max_drawdown < -0.25:
        findings.append("Maximum drawdown indicates elevated downside risk.")
    elif max_drawdown < -0.15:
        findings.append("Maximum drawdown is notable and should be monitored.")
    else:
        findings.append("Drawdown profile appears contained for the chosen window.")

    if top3 > 0.70:
        findings.append("Top-3 weight concentration is high, increasing single-theme risk.")
    else:
        findings.append("Top-3 concentration is within a moderate range.")

    if avg_corr > 0.60:
        findings.append("High average correlation suggests limited diversification benefit.")
    else:
        findings.append("Correlation structure provides reasonable diversification support.")

    return " ".join(findings)
