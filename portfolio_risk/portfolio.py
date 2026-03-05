"""
Portfolio management and calculations.
"""

import pandas as pd
import numpy as np


class Portfolio:
    """Represents an equity portfolio with defined weights and holdings."""
    
    def __init__(self, weights, returns_data):
        """
        Initialize Portfolio.
        
        Args:
            weights (dict or pd.Series): Portfolio weights {ticker: weight}.
                                         Weights should sum to 1.
            returns_data (pd.DataFrame): Historical returns data with tickers as columns.
        """
        if isinstance(weights, dict):
            self.weights = pd.Series(weights)
        else:
            self.weights = weights
        
        # Validate weights
        weight_sum = self.weights.sum()
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(f"Portfolio weights must sum to 1, got {weight_sum}")
        
        # Ensure returns data contains all tickers
        missing = set(self.weights.index) - set(returns_data.columns)
        if missing:
            raise ValueError(f"Missing data for tickers: {missing}")
        
        self.returns_data = returns_data[self.weights.index]
        self.tickers = list(self.weights.index)
        self.num_assets = len(self.tickers)
    
    def get_portfolio_returns(self):
        """
        Calculate portfolio returns as weighted sum of asset returns.
        
        Returns:
            pd.Series: Portfolio returns over time.
        """
        return (self.returns_data * self.weights).sum(axis=1)
    
    def get_expected_return(self):
        """
        Calculate expected annual portfolio return.
        
        Returns:
            float: Expected annual return (annualized).
        """
        mean_returns = self.returns_data.mean() * 252  # 252 trading days
        return np.sum(mean_returns * self.weights)
    
    def get_covariance_matrix(self):
        """
        Get covariance matrix of portfolio assets.
        
        Returns:
            pd.DataFrame: Annualized covariance matrix.
        """
        return self.returns_data.cov() * 252
    
    def get_portfolio_variance(self):
        """
        Calculate portfolio variance.
        
        Returns:
            float: Portfolio variance (annualized).
        """
        cov_matrix = self.get_covariance_matrix()
        return np.dot(self.weights.values, np.dot(cov_matrix.values, self.weights.values))
    
    def get_portfolio_volatility(self):
        """
        Calculate portfolio standard deviation (volatility).
        
        Returns:
            float: Portfolio volatility (annualized).
        """
        return np.sqrt(self.get_portfolio_variance())
    
    def get_weights(self):
        """Get portfolio weights."""
        return self.weights.copy()
    
    def set_weights(self, new_weights):
        """
        Update portfolio weights.
        
        Args:
            new_weights (dict or pd.Series): New portfolio weights.
        """
        if isinstance(new_weights, dict):
            new_weights = pd.Series(new_weights)
        
        weight_sum = new_weights.sum()
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(f"Portfolio weights must sum to 1, got {weight_sum}")
        
        self.weights = new_weights
    
    def get_summary(self):
        """
        Get portfolio summary statistics.
        
        Returns:
            dict: Dictionary containing key portfolio metrics.
        """
        return {
            'Expected Annual Return': self.get_expected_return(),
            'Annual Volatility': self.get_portfolio_volatility(),
            'Variance': self.get_portfolio_variance(),
            'Number of Assets': self.num_assets,
            'Tickers': self.tickers,
            'Weights': self.weights.to_dict(),
        }
