"""
Assignment 2: CSV Data Analysis with Functional Programming

This module demonstrates proficiency with functional programming paradigms
by performing various aggregation and grouping operations on sales data.

Features:
- CSV data loading and parsing
- Functional operations: map, filter, reduce, lambda
- Data aggregation: sum, average, min, max
- Grouping operations: group by category, region, date
"""

from .models import SalesRecord
from .data_loader import load_sales_data, load_sales_from_string
from .analysis import SalesAnalyzer

__all__ = ['SalesRecord', 'load_sales_data', 'load_sales_from_string', 'SalesAnalyzer']

