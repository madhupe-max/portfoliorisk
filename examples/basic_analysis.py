"""
Basic portfolio risk analysis example.

This script demonstrates how to use the portfolio_risk package to analyze
risk metrics for a sample portfolio.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio_risk import (
    DataLoader,
    Portfolio,
    RiskMetrics,
    CorrelationAnalyzer,
)


def main():
    """Run basic portfolio analysis."""
    
    # Define portfolio
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    weights = {
        'AAPL': 0.25,
        'MSFT': 0.25,
        'GOOGL': 0.20,
        'AMZN': 0.15,
        'TSLA': 0.15,
    }
    
    # Load historical data
    loader = DataLoader()
    prices = loader.fetch_data(tickers)
    returns = loader.get_returns(prices)
    
    # Create portfolio object
    portfolio = Portfolio(weights, returns)
    
    # Print portfolio summary
    print("\n" + "="*60)
    print("PORTFOLIO SUMMARY")
    print("="*60)
    summary = portfolio.get_summary()
    for key, value in summary.items():
        if key == 'Expected Annual Return':
            print(f"{key}: {value:.2%}")
        elif key == 'Annual Volatility':
            print(f"{key}: {value:.2%}")
        elif key == 'Weights':
            print(f"{key}:")
            for ticker, weight in value.items():
                print(f"  {ticker}: {weight:.1%}")
        else:
            print(f"{key}: {value}")
    
    # Calculate risk metrics
    print("\n" + "="*60)
    print("RISK METRICS")
    print("="*60)
    risk_summary = RiskMetrics.get_risk_summary(portfolio)
    for metric, value in risk_summary.items():
        if isinstance(value, float):
            if 'Return' in metric or 'Volatility' in metric or 'Drawdown' in metric:
                print(f"{metric}: {value:.2%}")
            else:
                print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: {value}")
    
    # Correlation analysis
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS")
    print("="*60)
    analyzer = CorrelationAnalyzer(returns)
    
    print(f"\nAverage Correlation: {analyzer.get_average_correlation():.4f}")
    
    print("\nTop Diversifiers for AAPL:")
    diversifiers = analyzer.find_diversifiers('AAPL', num_results=3)
    for ticker, corr in diversifiers.items():
        print(f"  {ticker}: {corr:.4f}")
    
    # Concentration metrics
    print("\nConcentration Metrics:")
    concentration = analyzer.get_concentration_report(portfolio.weights)
    for metric, value in concentration.items():
        if isinstance(value, float):
            if 'Weight' in metric or 'Concentration' in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.4f}")
        else:
            print(f"  {metric}: {value}")


if __name__ == '__main__':
    main()
