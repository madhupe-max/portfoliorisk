"""
Risk metrics calculation for portfolios.
"""

import numpy as np
import pandas as pd
from scipy import stats


class RiskMetrics:
    """Calculate various risk metrics for portfolios."""
    
    @staticmethod
    def value_at_risk(returns, confidence_level=0.95):
        """
        Calculate Value at Risk (VaR) using historical method.
        
        Args:
            returns (pd.Series): Portfolio returns.
            confidence_level (float): Confidence level (default: 0.95 for 95%).
        
        Returns:
            float: VaR value expressing maximum expected loss at given confidence.
        """
        return -np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def conditional_var(returns, confidence_level=0.95):
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall).
        
        Args:
            returns (pd.Series): Portfolio returns.
            confidence_level (float): Confidence level (default: 0.95 for 95%).
        
        Returns:
            float: CVaR value expressing expected loss beyond VaR.
        """
        var = RiskMetrics.value_at_risk(returns, confidence_level)
        return -returns[returns <= -var].mean()
    
    @staticmethod
    def sharpe_ratio(portfolio, risk_free_rate=0.02):
        """
        Calculate Sharpe ratio (excess return per unit of risk).
        
        Args:
            portfolio: Portfolio object with get_expected_return() and 
                      get_portfolio_volatility() methods.
            risk_free_rate (float): Annual risk-free rate (default: 0.02 = 2%).
        
        Returns:
            float: Sharpe ratio.
        """
        excess_return = portfolio.get_expected_return() - risk_free_rate
        volatility = portfolio.get_portfolio_volatility()
        
        if volatility == 0:
            return 0
        return excess_return / volatility
    
    @staticmethod
    def sortino_ratio(returns, target_return=0.0, risk_free_rate=0.02):
        """
        Calculate Sortino ratio (excess return per unit of downside risk).
        
        Args:
            returns (pd.Series): Portfolio returns.
            target_return (float): Target return for downside calculation (default: 0).
            risk_free_rate (float): Annual risk-free rate (default: 0.02).
        
        Returns:
            float: Sortino ratio.
        """
        excess_return = returns.mean() * 252 - risk_free_rate
        downside_returns = returns[returns < target_return]
        downside_volatility = np.sqrt((downside_returns ** 2).sum() / len(returns))
        downside_volatility_annual = downside_volatility * np.sqrt(252)
        
        if downside_volatility_annual == 0:
            return 0
        return excess_return / downside_volatility_annual
    
    @staticmethod
    def maximum_drawdown(returns):
        """
        Calculate maximum drawdown.
        
        Args:
            returns (pd.Series): Portfolio returns.
        
        Returns:
            float: Maximum drawdown (typically negative).
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def calmar_ratio(returns):
        """
        Calculate Calmar ratio (annual return / maximum drawdown).
        
        Args:
            returns (pd.Series): Portfolio returns.
        
        Returns:
            float: Calmar ratio.
        """
        annual_return = returns.mean() * 252
        max_dd = RiskMetrics.maximum_drawdown(returns)
        
        if abs(max_dd) == 0:
            return 0
        return annual_return / abs(max_dd)
    
    @staticmethod
    def beta(asset_returns, market_returns):
        """
        Calculate beta relative to market.
        
        Args:
            asset_returns (pd.Series): Asset returns.
            market_returns (pd.Series): Market returns (e.g., S&P 500).
        
        Returns:
            float: Beta coefficient.
        """
        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        return covariance / market_variance
    
    @staticmethod
    def get_risk_summary(portfolio, risk_free_rate=0.02):
        """
        Generate comprehensive risk summary for a portfolio.
        
        Args:
            portfolio: Portfolio object.
            risk_free_rate (float): Annual risk-free rate for Sharpe/Sortino (default: 0.02 = 2%).
        
        Returns:
            dict: Dictionary of key risk metrics.
        """
        returns = portfolio.get_portfolio_returns()
        
        return {
            'Annual Return': portfolio.get_expected_return(),
            'Annual Volatility': portfolio.get_portfolio_volatility(),
            'Sharpe Ratio': RiskMetrics.sharpe_ratio(portfolio, risk_free_rate=risk_free_rate),
            'Sortino Ratio': RiskMetrics.sortino_ratio(returns, risk_free_rate=risk_free_rate),
            'VaR (95%)': RiskMetrics.value_at_risk(returns, 0.95),
            'CVaR (95%)': RiskMetrics.conditional_var(returns, 0.95),
            'Maximum Drawdown': RiskMetrics.maximum_drawdown(returns),
            'Calmar Ratio': RiskMetrics.calmar_ratio(returns),
        }
