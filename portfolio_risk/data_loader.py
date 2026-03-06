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
        
        normalized_tickers = tickers if isinstance(tickers, list) else [tickers]
        data = yf.download(
            normalized_tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False,
        )

        if data.empty:
            raise ValueError("No price data returned for the provided tickers and date range")

        # yfinance can return either "Adj Close" or "Close" depending on settings/version.
        preferred_price_field = "Adj Close"
        fallback_price_field = "Close"

        if isinstance(data.columns, pd.MultiIndex):
            top_level_fields = set(data.columns.get_level_values(0))
            if preferred_price_field in top_level_fields:
                prices = data[preferred_price_field]
            elif fallback_price_field in top_level_fields:
                prices = data[fallback_price_field]
            else:
                raise ValueError(
                    "Could not find price field in downloaded data; expected 'Adj Close' or 'Close'"
                )
        else:
            if preferred_price_field in data.columns:
                prices = data[[preferred_price_field]].copy()
            elif fallback_price_field in data.columns:
                prices = data[[fallback_price_field]].copy()
            else:
                raise ValueError(
                    "Could not find price field in downloaded data; expected 'Adj Close' or 'Close'"
                )

            # For single ticker downloads, normalize to ticker-named column.
            prices.columns = [normalized_tickers[0]]

        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=normalized_tickers[0])

        return prices
    
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
