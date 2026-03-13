# Portfolio Risk Analysis Tool

A Python package for analyzing and quantifying risk in equity portfolios. This tool provides comprehensive risk metrics, correlation analysis, and portfolio optimization capabilities.

It now also includes a LangGraph-based agent workflow that orchestrates the existing analysis modules and returns a structured JSON risk report.

## Features

- **Data Management**: Automatic fetching of historical stock price data from Yahoo Finance
- **Portfolio Construction**: Easy-to-use portfolio class for managing asset weights and returns
- **Risk Metrics**: 
  - Value at Risk (VaR) and Conditional Value at Risk (CVaR)
  - Sharpe Ratio and Sortino Ratio
  - Maximum Drawdown and Calmar Ratio
  - Beta calculation
- **Correlation Analysis**: 
  - Asset correlation matrices
  - Diversification ratio and effective number of bets
  - Portfolio concentration metrics
- **Performance Analysis**: Expected return and volatility calculations

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or navigate to the project directory:
```bash
cd portfolio_risk
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Portfolio Analysis

```python
from portfolio_risk import DataLoader, Portfolio, RiskMetrics

# Define your portfolio
tickers = ['AAPL', 'MSFT', 'GOOGL']
weights = {'AAPL': 0.4, 'MSFT': 0.35, 'GOOGL': 0.25}

# Load historical data
loader = DataLoader(start_date='2022-01-01', end_date='2023-12-31')
prices = loader.fetch_data(tickers)
returns = loader.get_returns(prices)

# Create portfolio
portfolio = Portfolio(weights, returns)

# Analyze risk
metrics = RiskMetrics.get_risk_summary(portfolio)
print(f"Annual Return: {metrics['Annual Return']:.2%}")
print(f"Annual Volatility: {metrics['Annual Volatility']:.2%}")
print(f"Sharpe Ratio: {metrics['Sharpe Ratio']:.4f}")
print(f"Maximum Drawdown: {metrics['Maximum Drawdown']:.2%}")
```

### Correlation Analysis

```python
from portfolio_risk import CorrelationAnalyzer

analyzer = CorrelationAnalyzer(returns)

# Get correlation matrix
corr_matrix = analyzer.get_correlation_matrix()

# Find diversifiers
diversifiers = analyzer.find_diversifiers('AAPL', num_results=3)

# Check concentration
concentration = analyzer.get_concentration_report(portfolio.weights)
print(f"Effective Number of Bets: {concentration['Effective Number of Bets']:.2f}")
```

### LangGraph Agent Demo

Run the agent with the existing sample portfolio (AAPL, MSFT, GOOGL, AMZN, TSLA):

```bash
python examples/run_langgraph_agent.py --portfolio-file examples/sample_portfolio.json
```

Run with default built-in portfolio (same existing sample portfolio):

```bash
python examples/run_langgraph_agent.py
```

Run with custom options and save output:

```bash
python examples/run_langgraph_agent.py \
  --portfolio-file examples/sample_portfolio.json \
  --start-date 2024-01-01 \
  --end-date 2025-12-31 \
  --returns-method simple \
  --risk-free-rate 0.03 \
  --output-file outputs/agent_report.json
```

The agent output includes:
1. `portfolio` summary metrics
2. `risk` metrics (VaR, CVaR, Sharpe, Sortino, Drawdown, Calmar)
3. `correlation` and concentration analysis
4. `narrative` interpretation for quick review

### FastAPI HTTP Demo

Start the API server:

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

Run the API in Docker (build + run in one command):

```bash
docker run --rm -p 8000:8000 $(docker build -q .)
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Run analysis over HTTP using the existing sample portfolio:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d @examples/sample_portfolio.json
```

Run analysis with optional parameters:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.20, "AMZN": 0.15, "TSLA": 0.15},
    "start_date": "2024-01-01",
    "end_date": "2025-12-31",
    "returns_method": "simple",
    "risk_free_rate": 0.03
  }'
```

Interactive API docs are available at:
- `http://127.0.0.1:8000/docs`

## Project Structure

```
portfolio_risk/
├── Dockerfile                  # Linux-based API container image
├── .dockerignore               # Files excluded from Docker build context
├── api/
│   ├── __init__.py              # API package
│   └── app.py                   # FastAPI app and endpoints
├── agent/
│   ├── __init__.py              # Agent package exports
│   ├── config.py                # Defaults and constants
│   ├── state.py                 # Typed graph state
│   ├── tools.py                 # Wrappers around existing portfolio_risk modules
│   ├── prompts.py               # Narrative generation rules
│   └── portfolio_risk_agent.py  # LangGraph workflow and runner
├── portfolio_risk/
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # Data fetching and returns calculation
│   ├── portfolio.py             # Portfolio class and calculations
│   ├── risk_metrics.py          # Risk measurement functions
│   └── correlation.py           # Correlation and diversification analysis
├── examples/
│   └── basic_analysis.py        # Example usage script
│   ├── run_langgraph_agent.py   # Agent CLI runner
│   └── sample_portfolio.json    # Existing sample portfolio in JSON form
├── tests/                       # Unit tests directory
│   └── test_langgraph_agent.py  # Agent integration tests
├── specs/
│   ├── langgraph_portfolio_risk_agent_spec.md
│   └── python_coding_standards.md
├── requirements.txt             # Project dependencies
├── README.md                    # This file
└── .gitignore                  # Git ignore file
```

## LangGraph Agent Architecture

The agent composes your existing financial modules into a graph pipeline:

1. Resolve and validate portfolio input
2. Load market data and compute returns
3. Build `Portfolio` object
4. Compute risk metrics with `RiskMetrics`
5. Compute correlation/concentration with `CorrelationAnalyzer`
6. Generate narrative summary and return JSON

Primary implementation:
- `agent/portfolio_risk_agent.py`
- `examples/run_langgraph_agent.py`

HTTP wrapper:
- `api/app.py`

## Module Documentation

### DataLoader
Handles data fetching and preprocessing:
- `fetch_data(tickers)`: Download historical price data
- `get_returns(prices, method)`: Calculate simple or log returns

### Portfolio
Manages portfolio weights and calculations:
- `set_weights()`: Update portfolio allocation
- `get_expected_return()`: Expected annual return
- `get_portfolio_volatility()`: Portfolio standard deviation
- `get_covariance_matrix()`: Asset covariance matrix

### RiskMetrics
Comprehensive risk measurement toolkit:
- `value_at_risk()`: VaR calculation using historical method
- `conditional_var()`: Expected shortfall beyond VaR
- `sharpe_ratio()`: Return per unit of risk
- `sortino_ratio()`: Return per unit of downside risk
- `maximum_drawdown()`: Peak-to-trough decline
- `calmar_ratio()`: Return to drawdown ratio
- `get_risk_summary()`: Complete risk profile

### CorrelationAnalyzer
Diversification and correlation analysis:
- `get_correlation_matrix()`: Pairwise correlations
- `find_diversifiers()`: Find assets with low correlation
- `get_diversification_ratio()`: Measure diversification benefits
- `get_effective_number_of_bets()`: Portfolio concentration metric
- `get_concentration_report()`: Comprehensive concentration analysis

## Running the Example

Execute the basic analysis example:

```bash
python examples/basic_analysis.py
```

This will:
1. Download historical data for a sample portfolio (AAPL, MSFT, GOOGL, AMZN, TSLA)
2. Calculate portfolio metrics
3. Display risk analysis
4. Show correlation and concentration metrics

## Configuration

### Data Loading
Customize the date range for historical data:

```python
loader = DataLoader(start_date='2020-01-01', end_date='2024-01-01')
```

### Risk-Free Rate
Adjust the risk-free rate for Sharpe ratio calculation:

```python
sharpe = RiskMetrics.sharpe_ratio(portfolio, risk_free_rate=0.03)
```

### VaR Confidence Level
Modify the confidence level for Value at Risk:

```python
var_95 = RiskMetrics.value_at_risk(returns, confidence_level=0.95)
var_99 = RiskMetrics.value_at_risk(returns, confidence_level=0.99)
```

## Key Concepts

### Value at Risk (VaR)
Represents the maximum loss expected over a given time period at a specific confidence level.

### Conditional Value at Risk (CVaR)
Expected loss beyond the VaR threshold. More informative about tail risk than VaR alone.

### Sharpe Ratio
Measures excess return per unit of risk. Higher is better.

### Maximum Drawdown
The largest peak-to-trough decline. Indicates downside risk and recovery difficulty.

### Diversification Ratio
Ratio of weighted average volatility to portfolio volatility. Higher indicates better diversification.

### Effective Number of Bets
Indicates portfolio concentration. Equal to 1/(sum of squared weights). Higher values indicate more diversification.

## Dependencies

- **numpy**: Numerical computations
- **pandas**: Data manipulation and analysis
- **scipy**: Statistical functions
- **matplotlib**: Data visualization (for future enhancements)
- **yfinance**: Financial data download
- **langgraph**: Agent workflow orchestration
- **langchain / langchain-core**: Graph runtime dependencies
- **pydantic**: Structured validation/modeling support
- **fastapi**: HTTP API framework
- **uvicorn**: ASGI server for local API hosting

## Future Enhancements

- [ ] Visualization module for portfolio charts
- [ ] Portfolio optimization algorithms
- [ ] Monte Carlo simulation for forecasting
- [ ] Factor analysis and attribution
- [ ] Backtesting framework
- [ ] Real-time portfolio monitoring
- [ ] Advanced risk models (GARCH, etc.)

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Functions have proper docstrings
- Tests are provided for new features

## License

This project is provided as-is for educational and analysis purposes.

## Support

For issues, questions, or suggestions, please refer to the project documentation or create an issue in the repository.

---

**Version**: 0.1.0  
**Last Updated**: 2024
