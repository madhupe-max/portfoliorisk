# Python Coding Standards (Supplementary)

This document defines coding standards for implementing and maintaining the LangGraph portfolio risk agent.

## 1. Python Version and Environment
- Target Python 3.10+.
- Use an isolated virtual environment for development and CI.
- Pin minimum dependency versions in requirements files.

## 2. Style and Formatting
- Follow PEP 8 for naming and layout.
- Use 4 spaces for indentation.
- Keep line length to 100 characters where practical.
- Prefer explicit imports over wildcard imports.
- Group imports in this order with a blank line between groups:
  1. standard library
  2. third-party
  3. local application imports

## 3. Naming Conventions
- Modules/files: `snake_case.py`
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: prefix with `_`

## 4. Type Hints and Data Models
- Add type hints to all public functions and methods.
- Use `TypedDict` or `pydantic` models for graph state and structured payloads.
- Avoid `Any` unless unavoidable; document why when used.
- Prefer concrete types (`dict[str, float]`) over generic containers when known.

## 5. Function and Class Design
- Keep functions focused and side-effect aware.
- Prefer pure functions for calculations.
- Keep orchestration logic in graph nodes; keep financial formulas in domain modules.
- Raise specific exceptions with clear messages.

## 6. Documentation and Comments
- Include docstrings for all public modules, classes, and functions.
- Use Google-style or consistent project style for docstrings.
- Add comments only where business logic is non-obvious.
- Keep comments current with code changes.

## 7. Error Handling
- Validate input early (tickers, weights, date format, required fields).
- Fail fast on invalid state transitions.
- Use structured error payloads with `error_code`, `message`, and `recoverable`.
- Never silently swallow exceptions; log and propagate with context.

## 8. Logging and Observability
- Use the `logging` module instead of `print` in new code.
- Log at appropriate levels:
  - `DEBUG` for intermediate calculations and graph transitions
  - `INFO` for lifecycle milestones
  - `WARNING` for recoverable issues
  - `ERROR` for failed execution paths
- Do not log secrets or sensitive account data.

## 9. Testing Standards
- Use `pytest` for all tests.
- Cover both success and failure paths for each graph node.
- Add integration tests for full-graph execution with default portfolio.
- Use deterministic fixtures and avoid flaky network tests where possible.
- When external data is required, mock `yfinance` in unit tests.

## 10. Project-Specific Rules
- Reuse existing package logic:
  - `portfolio_risk.data_loader.DataLoader`
  - `portfolio_risk.portfolio.Portfolio`
  - `portfolio_risk.risk_metrics.RiskMetrics`
  - `portfolio_risk.correlation.CorrelationAnalyzer`
- Do not duplicate financial metric formulas in the agent layer.
- Keep node outputs JSON-serializable at graph boundaries.

## 11. Security and Reliability
- Validate all file path inputs before loading portfolio definitions.
- Limit accepted input schema to expected keys and value ranges.
- Set reasonable timeouts/retries around network-dependent data fetches.

## 12. Recommended Tooling
- Formatter: `black`
- Linter: `ruff`
- Type checker: `mypy`
- Tests: `pytest`

Suggested local commands:
```bash
ruff check .
black .
mypy portfolio_risk agent
pytest -q
```

## 13. Definition of Done (Code Quality)
A change is complete only if:
1. Code is formatted and lint-clean.
2. Type checks pass for modified modules.
3. Tests pass for modified behavior.
4. Public APIs and output contracts remain backward compatible unless explicitly versioned.
