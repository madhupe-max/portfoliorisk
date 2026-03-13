# LangGraph Agent Spec: Portfolio Risk Analysis

## 1. Purpose
Build a LangGraph-based agent that orchestrates the existing portfolio risk analysis capabilities in this project and returns:
- Portfolio summary (expected return, volatility, variance, composition)
- Risk metrics (VaR, CVaR, Sharpe, Sortino, Max Drawdown, Calmar)
- Correlation/diversification metrics
- Human-readable risk commentary and recommendations

This spec uses the existing sample portfolio from `examples/basic_analysis.py` as the default runnable portfolio.

## 2. Existing Portfolio (Baseline)
Use this portfolio for default analysis and integration testing:
- Tickers: AAPL, MSFT, GOOGL, AMZN, TSLA
- Weights:
  - AAPL: 0.25
  - MSFT: 0.25
  - GOOGL: 0.20
  - AMZN: 0.15
  - TSLA: 0.15
- Date range: Default DataLoader range (last 365 days) unless user provides start/end dates.

## 3. Scope
### In scope
- Build a LangGraph workflow around existing modules:
  - `portfolio_risk/data_loader.py`
  - `portfolio_risk/portfolio.py`
  - `portfolio_risk/risk_metrics.py`
  - `portfolio_risk/correlation.py`
- Support user-provided portfolio OR default baseline portfolio.
- Produce machine-readable JSON output and narrative summary.
- Include robust error handling and validation.

### Out of scope (v1)
- Portfolio optimization/rebalancing
- Monte Carlo simulation
- Real-time streaming prices
- Broker/API trade execution

## 4. Functional Requirements
1. Agent accepts input:
   - `tickers` (list[str]) optional
   - `weights` (dict[str, float]) optional
   - `start_date` (YYYY-MM-DD) optional
   - `end_date` (YYYY-MM-DD) optional
   - `returns_method` (`simple` or `log`) optional, default `simple`
   - `risk_free_rate` optional, default 0.02
2. If no tickers/weights are provided, use baseline portfolio.
3. Validate weights sum to 1.0 (within tolerance).
4. Fetch prices via existing `DataLoader.fetch_data`.
5. Compute returns via `DataLoader.get_returns`.
6. Construct `Portfolio` object and compute summary.
7. Compute risk metrics using `RiskMetrics.get_risk_summary`.
8. Compute correlation and concentration via `CorrelationAnalyzer`.
9. Generate narrative output with key findings:
   - strongest risk concerns
   - concentration findings
   - diversification notes
10. Return final structured output with timestamps and execution status.

## 5. Non-Functional Requirements
- Deterministic calculations for a given price dataset.
- Clear failure modes with actionable errors.
- Runtime target: under 10 seconds for 5-20 tickers (network-dependent).
- Extensible graph nodes for future analytics.

## 6. Dependencies
Add these dependencies:
- `langgraph`
- `langchain`
- `langchain-core`
- `pydantic`

Keep existing dependencies from `requirements.txt`:
- numpy, pandas, scipy, matplotlib, yfinance

Recommended `requirements-agent.txt` additions:
- langgraph>=0.2.0
- langchain>=0.3.0
- langchain-core>=0.3.0
- pydantic>=2.0.0

## 7. Proposed File Layout
Create:
- `agent/portfolio_risk_agent.py` (graph definition and runner)
- `agent/state.py` (state schema)
- `agent/tools.py` (thin wrappers over existing project classes)
- `agent/prompts.py` (narrative/report prompt templates)
- `agent/config.py` (defaults and constants)
- `examples/run_langgraph_agent.py` (CLI entry point)
- `tests/test_langgraph_agent.py` (integration tests)

## 8. LangGraph Design
### 8.1 State Model
Use a TypedDict or Pydantic model.

Required state fields:
- `input_portfolio`: dict
- `tickers`: list[str]
- `weights`: dict[str, float]
- `start_date`: str | None
- `end_date`: str | None
- `returns_method`: str
- `risk_free_rate`: float
- `prices`: pandas.DataFrame | None
- `returns`: pandas.DataFrame | None
- `portfolio_summary`: dict | None
- `risk_summary`: dict | None
- `correlation_summary`: dict | None
- `narrative`: str | None
- `warnings`: list[str]
- `errors`: list[str]
- `status`: str (`initialized`, `running`, `completed`, `failed`)

### 8.2 Node Contracts
1. `resolve_input_node`
- Input: raw user payload
- Output: normalized tickers/weights/defaults

2. `validate_input_node`
- Validate:
  - non-empty tickers
  - weights length matches tickers
  - weights approximately sum to 1.0
  - date format if provided
- On error, route to `error_node`

3. `load_market_data_node`
- Call `DataLoader(start_date, end_date).fetch_data(tickers)`
- Call `get_returns(prices, method=returns_method)`
- Store prices/returns in state

4. `build_portfolio_node`
- Create `Portfolio(weights, returns)`
- Store summary from `portfolio.get_summary()`

5. `compute_risk_metrics_node`
- `RiskMetrics.get_risk_summary(portfolio)`
- If risk_free_rate from input differs from default, recompute Sharpe/Sortino using custom rate and override fields

6. `compute_correlation_node`
- `CorrelationAnalyzer(returns)`
- Collect:
  - average correlation
  - diversifiers for first ticker (`num_results=3`)
  - concentration report

7. `generate_report_node`
- Build concise narrative from summary metrics with threshold-based interpretation.
- Example interpretation rules:
  - `Sharpe Ratio < 0.5`: weak risk-adjusted return
  - `Maximum Drawdown < -0.25`: high downside risk
  - `Top 3 Concentration > 0.70`: concentration risk warning

8. `finalize_node`
- Assemble final JSON with status, computed sections, warnings/errors.

9. `error_node`
- Set status `failed`
- Return partial state and errors.

### 8.3 Graph Edges
- START -> resolve_input_node -> validate_input_node
- validate_input_node -> load_market_data_node (if valid)
- validate_input_node -> error_node (if invalid)
- load_market_data_node -> build_portfolio_node
- build_portfolio_node -> compute_risk_metrics_node
- compute_risk_metrics_node -> compute_correlation_node
- compute_correlation_node -> generate_report_node
- generate_report_node -> finalize_node -> END
- Any runtime exception -> error_node -> END

## 9. Output Contract (JSON)
The agent should return:

```
{
  "status": "completed",
  "as_of": "2026-03-13",
  "portfolio": {
    "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.20, "AMZN": 0.15, "TSLA": 0.15},
    "summary": {
      "Expected Annual Return": 0.00,
      "Annual Volatility": 0.00,
      "Variance": 0.00,
      "Number of Assets": 5
    }
  },
  "risk": {
    "Annual Return": 0.00,
    "Annual Volatility": 0.00,
    "Sharpe Ratio": 0.00,
    "Sortino Ratio": 0.00,
    "VaR (95%)": 0.00,
    "CVaR (95%)": 0.00,
    "Maximum Drawdown": 0.00,
    "Calmar Ratio": 0.00
  },
  "correlation": {
    "average_correlation": 0.00,
    "diversifiers": {},
    "concentration": {
      "Largest Weight": 0.25,
      "Top 3 Concentration": 0.70,
      "Herfindahl Index": 0.00,
      "Effective Number of Bets": 0.00,
      "Average Correlation": 0.00
    }
  },
  "narrative": "...",
  "warnings": [],
  "errors": []
}
```

## 10. CLI/API Behavior
### CLI
`python examples/run_langgraph_agent.py`

Optional flags:
- `--portfolio-file path/to/portfolio.json`
- `--start-date YYYY-MM-DD`
- `--end-date YYYY-MM-DD`
- `--returns-method simple|log`
- `--risk-free-rate 0.02`
- `--output-file path/to/report.json`

### Portfolio JSON schema
```
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.20,
    "AMZN": 0.15,
    "TSLA": 0.15
  }
}
```

## 11. Error Handling Requirements
- Validation errors:
  - invalid or missing tickers
  - missing weights
  - weights not summing to 1
  - mismatch tickers vs weight keys
- Data errors:
  - no market data for date range/tickers
  - partial ticker data missing
- Compute errors:
  - empty returns set
  - divide-by-zero conditions handled safely

Each error should include:
- `error_code`
- `message`
- `recoverable` (bool)
- optional `details`

## 12. Testing Requirements
### Unit tests
- Input normalization and validation node behavior
- Edge routing behavior for valid vs invalid inputs
- Report-generation rule logic

### Integration tests
1. Baseline portfolio run (default inputs) returns `status=completed`.
2. Invalid weights run returns `status=failed` and descriptive error.
3. Custom date range run returns non-empty risk metrics.

### Regression tests
- Ensure output keys remain stable for downstream consumers.

## 13. Acceptance Criteria
1. Running default agent command executes full graph and returns completed status.
2. Output includes `portfolio`, `risk`, `correlation`, and `narrative` sections.
3. Values come from existing `portfolio_risk` module calculations (no duplicated financial formulas in agent layer).
4. Invalid input is rejected before market data fetch.
5. Test suite includes at least one successful and one failure path.

## 14. Implementation Plan (Suggested)
1. Add dependencies and create `agent/` package skeleton.
2. Implement state schema and validation helpers.
3. Implement LangGraph nodes and edges.
4. Add CLI runner using default baseline portfolio.
5. Add tests and run full validation.
6. Add docs snippet in README linking to the new agent workflow.

## 15. Future Extensions
- Add scenario stress testing node.
- Add optional benchmark beta vs SPY.
- Add node for optimization suggestions based on concentration and correlation thresholds.
- Add LLM-generated executive summary variant for business users.

## 16. Supplementary Standards
- Python coding standards for this implementation are defined in `specs/python_coding_standards.md`.
