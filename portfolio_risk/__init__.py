"""
Portfolio Risk Analysis Tool

A Python package for analyzing and quantifying risk in equity portfolios.
"""

from .portfolio import Portfolio
from .risk_metrics import RiskMetrics
from .data_loader import DataLoader
from .correlation import CorrelationAnalyzer

__version__ = "0.1.0"
__author__ = "Portfolio Risk Analysis Team"

__all__ = [
    "Portfolio",
    "RiskMetrics",
    "DataLoader",
    "CorrelationAnalyzer",
]
