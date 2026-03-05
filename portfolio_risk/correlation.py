"""
Correlation and diversification analysis.
"""

import pandas as pd
import numpy as np


class CorrelationAnalyzer:
    """Analyze correlations and diversification benefits in a portfolio."""
    
    def __init__(self, returns_data):
        """
        Initialize CorrelationAnalyzer.
        
        Args:
            returns_data (pd.DataFrame): Historical returns data with tickers as columns.
        """
        self.returns_data = returns_data
        self.correlation_matrix = returns_data.corr()
    
    def get_correlation_matrix(self):
        """
        Get correlation matrix of all assets.
        
        Returns:
            pd.DataFrame: Correlation matrix.
        """
        return self.correlation_matrix.copy()
    
    def get_pairwise_correlation(self, ticker1, ticker2):
        """
        Get correlation between two specific assets.
        
        Args:
            ticker1 (str): First ticker symbol.
            ticker2 (str): Second ticker symbol.
        
        Returns:
            float: Correlation coefficient.
        """
        return self.correlation_matrix.loc[ticker1, ticker2]
    
    def get_average_correlation(self):
        """
        Get average correlation across all asset pairs.
        
        Returns:
            float: Average correlation.
        """
        # Get upper triangle of correlation matrix (exclude diagonal)
        mask = np.triu(np.ones_like(self.correlation_matrix, dtype=bool), k=1)
        return self.correlation_matrix.values[mask].mean()
    
    def find_diversifiers(self, reference_ticker, num_results=5):
        """
        Find assets with lowest correlation to a reference asset.
        
        Args:
            reference_ticker (str): Reference ticker symbol.
            num_results (int): Number of results to return.
        
        Returns:
            pd.Series: Assets sorted by correlation (lowest first).
        """
        correlations = self.correlation_matrix[reference_ticker].drop(reference_ticker)
        return correlations.nsmallest(num_results)
    
    def get_diversification_ratio(self, weights, volatilities):
        """
        Calculate diversification ratio (sum of weighted volatilities / portfolio volatility).
        
        Args:
            weights (pd.Series): Portfolio weights.
            volatilities (pd.Series): Individual asset volatilities (annualized).
        
        Returns:
            float: Diversification ratio (higher is better).
        """
        numerator = (weights * volatilities).sum()
        
        # Calculate portfolio volatility
        cov_matrix = self.returns_data.cov() * 252
        portfolio_vol = np.sqrt(np.dot(weights.values, np.dot(cov_matrix, weights.values)))
        
        if portfolio_vol == 0:
            return 0
        return numerator / portfolio_vol
    
    def get_effective_number_of_bets(self, weights):
        """
        Calculate effective number of bets (measure of portfolio concentration).
        
        Args:
            weights (pd.Series): Portfolio weights.
        
        Returns:
            float: Effective number of independent bets (higher = more diversified).
        """
        herfindahl = (weights ** 2).sum()
        if herfindahl == 0:
            return 0
        return 1 / herfindahl
    
    def get_concentration_report(self, weights):
        """
        Generate concentration metrics for the portfolio.
        
        Args:
            weights (pd.Series): Portfolio weights.
        
        Returns:
            dict: Dictionary of concentration metrics.
        """
        return {
            'Largest Weight': weights.max(),
            'Top 3 Concentration': weights.nlargest(3).sum(),
            'Herfindahl Index': (weights ** 2).sum(),
            'Effective Number of Bets': self.get_effective_number_of_bets(weights),
            'Average Correlation': self.get_average_correlation(),
        }
