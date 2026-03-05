"""
Data loading module for fetching stock price data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class DataLoader:
    """Load historical stock price data for portfolio analysis."""
    
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize DataLoader.
        
        Args:
            start_date (str or datetime): Start date for data (YYYY-MM-DD format).
                                         Defaults to 1 year ago.
            end_date (str or datetime): End date for data (YYYY-MM-DD format).
                                       Defaults to today.
        """
        if end_date is None:
            self.end_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.end_date = end_date
            
        if start_date is None:
            self.start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            self.start_date = start_date
    
    def fetch_data(self, tickers):
        """
        Fetch historical price data for given tickers.
        
        Args:
            tickers (list): List of ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL']).
        
        Returns:
            pd.DataFrame: Adjusted close prices with tickers as columns.
        """
        print(f"Fetching data for {tickers} from {self.start_date} to {self.end_date}...")
        
        data = yf.download(tickers, start=self.start_date, end=self.end_date, 
                          progress=False)
        
        # Handle single ticker case
        if isinstance(data.columns, pd.RangeIndex):
            data = data[['Adj Close']]
            data.columns = [tickers[0] if isinstance(tickers, list) else tickers]
        else:
            data = data['Adj Close']
        
        return data
    
    def get_returns(self, prices, method='simple'):
        """
        Calculate returns from price data.
        
        Args:
            prices (pd.DataFrame): Historical price data.
            method (str): 'simple' for simple returns or 'log' for log returns.
        
        Returns:
            pd.DataFrame: Returns data.
        """
        if method == 'simple':
            returns = prices.pct_change().dropna()
        elif method == 'log':
            returns = np.log(prices / prices.shift(1)).dropna()
        else:
            raise ValueError("method must be 'simple' or 'log'")
        
        return returns
