"""
Sales Data Analysis Module

Provides analytical operations on sales data using functional programming:
- map, filter, reduce operations
- Lambda expressions
- functools.partial for reusable functions
- Data aggregation (sum, average, min, max, median, std dev)
- Grouping operations (group by category, region, etc.)
"""

from functools import reduce, partial
from itertools import groupby
from typing import List, Dict, Callable, Any, Tuple, Optional
from collections import defaultdict
from datetime import date
import math
from .models import SalesRecord


# ==================== PARTIAL FUNCTION HELPERS ====================
# Using functools.partial to create reusable, specialized functions

def _get_attribute(attr_name: str, record: SalesRecord) -> Any:
    """Generic attribute getter for use with partial."""
    return getattr(record, attr_name)

def _compare_attribute(attr_name: str, value: Any, record: SalesRecord) -> bool:
    """Generic attribute comparator for use with partial."""
    return getattr(record, attr_name) == value

def _compare_amount_gte(threshold: float, record: SalesRecord) -> bool:
    """Compare if record's total_amount >= threshold."""
    return record.total_amount >= threshold

# Pre-built partial functions for common operations
get_amount = partial(_get_attribute, 'total_amount')
get_quantity = partial(_get_attribute, 'quantity')
get_category = partial(_get_attribute, 'category')
get_region = partial(_get_attribute, 'region')
get_product = partial(_get_attribute, 'product_name')
get_salesperson = partial(_get_attribute, 'salesperson')

# Partial function factory for creating filters
def make_category_filter(category: str) -> Callable[[SalesRecord], bool]:
    """Create a category filter using partial application."""
    return partial(_compare_attribute, 'category', category)

def make_region_filter(region: str) -> Callable[[SalesRecord], bool]:
    """Create a region filter using partial application."""
    return partial(_compare_attribute, 'region', region)

def make_min_amount_filter(threshold: float) -> Callable[[SalesRecord], bool]:
    """Create a minimum amount filter using partial application."""
    return partial(_compare_amount_gte, threshold)


class SalesAnalyzer:
    """
    Analyzer for sales data using functional programming paradigms.
    
    All analysis methods use functional operations like map, filter,
    reduce, and lambda expressions.
    """
    
    def __init__(self, records: List[SalesRecord]):
        """
        Initialize analyzer with sales records.
        
        Args:
            records: List of SalesRecord objects to analyze.
        """
        self._records = records
    
    @property
    def records(self) -> List[SalesRecord]:
        """Return the list of records."""
        return self._records
    
    @property
    def count(self) -> int:
        """Return total number of records."""
        return len(self._records)
    
    # ==================== BASIC AGGREGATIONS ====================
    
    def total_revenue(self) -> float:
        """
        Calculate total revenue across all transactions.
        
        Uses: reduce with lambda
        """
        return reduce(
            lambda acc, record: acc + record.total_amount,
            self._records,
            0.0
        )
    
    def total_quantity(self) -> int:
        """
        Calculate total quantity of items sold.
        
        Uses: sum with map and lambda
        """
        return sum(map(lambda r: r.quantity, self._records))
    
    def average_transaction_value(self) -> float:
        """
        Calculate average transaction value.
        
        Uses: reduce for sum, then division
        """
        if not self._records:
            return 0.0
        total = reduce(lambda acc, r: acc + r.total_amount, self._records, 0.0)
        return total / len(self._records)
    
    def min_transaction(self) -> Optional[SalesRecord]:
        """
        Find transaction with minimum value.
        
        Uses: min with key lambda
        """
        if not self._records:
            return None
        return min(self._records, key=lambda r: r.total_amount)
    
    def max_transaction(self) -> Optional[SalesRecord]:
        """
        Find transaction with maximum value.
        
        Uses: max with key lambda
        """
        if not self._records:
            return None
        return max(self._records, key=lambda r: r.total_amount)
    
    # ==================== ADVANCED STATISTICS ====================
    
    def median_transaction_value(self) -> float:
        """
        Calculate median transaction value.
        
        Uses: sorted with lambda, functional approach
        
        Returns:
            Median value, or 0.0 if no records.
        """
        if not self._records:
            return 0.0
        
        # Use partial function to extract amounts
        amounts = sorted(map(get_amount, self._records))
        n = len(amounts)
        
        if n % 2 == 1:
            return amounts[n // 2]
        else:
            # Average of two middle values
            mid = n // 2
            return (amounts[mid - 1] + amounts[mid]) / 2
    
    def variance(self) -> float:
        """
        Calculate variance of transaction values.
        
        Uses: reduce for sum of squared differences
        
        Returns:
            Population variance, or 0.0 if no records.
        """
        if not self._records:
            return 0.0
        
        mean = self.average_transaction_value()
        n = len(self._records)
        
        # Sum of squared differences using reduce
        sum_sq_diff = reduce(
            lambda acc, r: acc + (r.total_amount - mean) ** 2,
            self._records,
            0.0
        )
        
        return sum_sq_diff / n
    
    def std_deviation(self) -> float:
        """
        Calculate standard deviation of transaction values.
        
        Uses: variance calculation with sqrt
        
        Returns:
            Population standard deviation, or 0.0 if no records.
        """
        return math.sqrt(self.variance())
    
    def percentile(self, p: float) -> float:
        """
        Calculate the p-th percentile of transaction values.
        
        Uses: sorted with partial function, functional approach
        
        Args:
            p: Percentile value (0-100)
        
        Returns:
            The p-th percentile value, or 0.0 if no records.
        """
        if not self._records or not (0 <= p <= 100):
            return 0.0
        
        amounts = sorted(map(get_amount, self._records))
        n = len(amounts)
        
        # Calculate index
        idx = (p / 100) * (n - 1)
        lower = int(idx)
        upper = min(lower + 1, n - 1)
        
        # Linear interpolation
        weight = idx - lower
        return amounts[lower] * (1 - weight) + amounts[upper] * weight
    
    def quartiles(self) -> Dict[str, float]:
        """
        Calculate Q1, Q2 (median), and Q3 quartiles.
        
        Uses: percentile function with partial application pattern
        
        Returns:
            Dictionary with Q1, Q2, Q3 values.
        """
        # Using partial-like pattern for percentile calculation
        calc_percentile = lambda p: self.percentile(p)
        
        return {
            "Q1": calc_percentile(25),
            "Q2": calc_percentile(50),  # Median
            "Q3": calc_percentile(75),
            "IQR": calc_percentile(75) - calc_percentile(25)  # Interquartile range
        }
    
    def coefficient_of_variation(self) -> float:
        """
        Calculate coefficient of variation (CV).
        
        CV = (std_deviation / mean) * 100
        
        Returns:
            CV as percentage, or 0.0 if mean is 0.
        """
        mean = self.average_transaction_value()
        if mean == 0:
            return 0.0
        return (self.std_deviation() / mean) * 100
    
    # ==================== FILTERING OPERATIONS ====================
    
    def filter_by(self, predicate: Callable[[SalesRecord], bool]) -> 'SalesAnalyzer':
        """
        Filter records by a predicate function.
        
        Uses: filter with custom predicate
        
        Args:
            predicate: Function returning True for records to include.
        
        Returns:
            New SalesAnalyzer with filtered records.
        """
        filtered = list(filter(predicate, self._records))
        return SalesAnalyzer(filtered)
    
    def filter_by_category(self, category: str) -> 'SalesAnalyzer':
        """
        Filter records by product category.
        
        Uses: filter with lambda
        """
        return self.filter_by(lambda r: r.category == category)
    
    def filter_by_region(self, region: str) -> 'SalesAnalyzer':
        """
        Filter records by sales region.
        
        Uses: filter with lambda
        """
        return self.filter_by(lambda r: r.region == region)
    
    def filter_by_date_range(self, start: date, end: date) -> 'SalesAnalyzer':
        """
        Filter records within a date range.
        
        Uses: filter with compound lambda
        """
        return self.filter_by(lambda r: start <= r.date <= end)
    
    def filter_by_min_amount(self, min_amount: float) -> 'SalesAnalyzer':
        """
        Filter records with total amount >= min_amount.
        
        Uses: filter with lambda
        """
        return self.filter_by(lambda r: r.total_amount >= min_amount)
    
    def filter_by_salesperson(self, salesperson: str) -> 'SalesAnalyzer':
        """
        Filter records by salesperson name.
        
        Uses: filter with lambda
        """
        return self.filter_by(lambda r: r.salesperson == salesperson)
    
    # ==================== PARTIAL FUNCTION FILTERING ====================
    
    def filter_by_category_partial(self, category: str) -> 'SalesAnalyzer':
        """
        Filter records by category using partial function.
        
        Uses: functools.partial for reusable filter creation
        
        This demonstrates an alternative to lambda using partial application.
        """
        category_filter = make_category_filter(category)
        return self.filter_by(category_filter)
    
    def filter_by_region_partial(self, region: str) -> 'SalesAnalyzer':
        """
        Filter records by region using partial function.
        
        Uses: functools.partial for reusable filter creation
        """
        region_filter = make_region_filter(region)
        return self.filter_by(region_filter)
    
    def filter_by_min_amount_partial(self, threshold: float) -> 'SalesAnalyzer':
        """
        Filter records by minimum amount using partial function.
        
        Uses: functools.partial for threshold comparison
        """
        amount_filter = make_min_amount_filter(threshold)
        return self.filter_by(amount_filter)
    
    # ==================== GROUPING OPERATIONS ====================
    
    def group_by(self, key_func: Callable[[SalesRecord], Any]) -> Dict[Any, List[SalesRecord]]:
        """
        Group records by a key function.
        
        Uses: defaultdict with functional iteration
        
        Args:
            key_func: Function to extract grouping key from record.
        
        Returns:
            Dictionary mapping keys to lists of records.
        """
        groups: Dict[Any, List[SalesRecord]] = defaultdict(list)
        # Functional approach using map to create (key, record) pairs
        for key, record in map(lambda r: (key_func(r), r), self._records):
            groups[key].append(record)
        return dict(groups)
    
    def group_by_category(self) -> Dict[str, List[SalesRecord]]:
        """Group records by product category."""
        return self.group_by(lambda r: r.category)
    
    def group_by_region(self) -> Dict[str, List[SalesRecord]]:
        """Group records by sales region."""
        return self.group_by(lambda r: r.region)
    
    def group_by_salesperson(self) -> Dict[str, List[SalesRecord]]:
        """Group records by salesperson."""
        return self.group_by(lambda r: r.salesperson)
    
    def group_by_product(self) -> Dict[str, List[SalesRecord]]:
        """Group records by product name."""
        return self.group_by(lambda r: r.product_name)
    
    def group_by_date(self) -> Dict[date, List[SalesRecord]]:
        """Group records by transaction date."""
        return self.group_by(lambda r: r.date)
    
    # ==================== AGGREGATION BY GROUP ====================
    
    def revenue_by_category(self) -> Dict[str, float]:
        """
        Calculate total revenue per category.
        
        Uses: groupby + reduce
        """
        groups = self.group_by_category()
        # Functional: map each group to (category, sum)
        return dict(map(
            lambda item: (
                item[0],
                reduce(lambda acc, r: acc + r.total_amount, item[1], 0.0)
            ),
            groups.items()
        ))
    
    def revenue_by_region(self) -> Dict[str, float]:
        """
        Calculate total revenue per region.
        
        Uses: groupby + reduce
        """
        groups = self.group_by_region()
        return dict(map(
            lambda item: (
                item[0],
                reduce(lambda acc, r: acc + r.total_amount, item[1], 0.0)
            ),
            groups.items()
        ))
    
    def revenue_by_salesperson(self) -> Dict[str, float]:
        """
        Calculate total revenue per salesperson.
        
        Uses: groupby + reduce
        """
        groups = self.group_by_salesperson()
        return dict(map(
            lambda item: (
                item[0],
                reduce(lambda acc, r: acc + r.total_amount, item[1], 0.0)
            ),
            groups.items()
        ))
    
    def quantity_by_product(self) -> Dict[str, int]:
        """
        Calculate total quantity sold per product.
        
        Uses: groupby + sum + map
        """
        groups = self.group_by_product()
        return dict(map(
            lambda item: (item[0], sum(map(lambda r: r.quantity, item[1]))),
            groups.items()
        ))
    
    def average_by_category(self) -> Dict[str, float]:
        """
        Calculate average transaction value per category.
        
        Uses: groupby + reduce + map
        """
        groups = self.group_by_category()
        return dict(map(
            lambda item: (
                item[0],
                reduce(lambda acc, r: acc + r.total_amount, item[1], 0.0) / len(item[1])
                if item[1] else 0.0
            ),
            groups.items()
        ))
    
    def count_by_region(self) -> Dict[str, int]:
        """
        Count transactions per region.
        
        Uses: groupby + len
        """
        groups = self.group_by_region()
        return dict(map(lambda item: (item[0], len(item[1])), groups.items()))
    
    # ==================== TRANSFORMATION OPERATIONS ====================
    
    def get_all_amounts(self) -> List[float]:
        """
        Extract all transaction amounts.
        
        Uses: map with lambda
        """
        return list(map(lambda r: r.total_amount, self._records))
    
    def get_unique_categories(self) -> List[str]:
        """
        Get unique product categories.
        
        Uses: set + map
        """
        return list(set(map(lambda r: r.category, self._records)))
    
    def get_unique_regions(self) -> List[str]:
        """
        Get unique sales regions.
        
        Uses: set + map
        """
        return list(set(map(lambda r: r.region, self._records)))
    
    def get_unique_products(self) -> List[str]:
        """
        Get unique product names.
        
        Uses: set + map
        """
        return list(set(map(lambda r: r.product_name, self._records)))
    
    def get_unique_salespersons(self) -> List[str]:
        """
        Get unique salesperson names.
        
        Uses: set + map
        """
        return list(set(map(lambda r: r.salesperson, self._records)))
    
    # ==================== RANKING OPERATIONS ====================
    
    def top_products_by_revenue(self, n: int = 5) -> List[Tuple[str, float]]:
        """
        Get top N products by total revenue.
        
        Uses: groupby + reduce + sorted with lambda
        """
        product_revenue = dict(map(
            lambda item: (
                item[0],
                reduce(lambda acc, r: acc + r.total_amount, item[1], 0.0)
            ),
            self.group_by_product().items()
        ))
        # Sort by revenue descending
        sorted_products = sorted(
            product_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_products[:n]
    
    def top_salespersons_by_revenue(self, n: int = 5) -> List[Tuple[str, float]]:
        """
        Get top N salespersons by total revenue.
        
        Uses: sorted with lambda key
        """
        revenue = self.revenue_by_salesperson()
        return sorted(revenue.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def top_transactions(self, n: int = 5) -> List[SalesRecord]:
        """
        Get top N transactions by value.
        
        Uses: sorted with lambda key
        """
        return sorted(self._records, key=lambda r: r.total_amount, reverse=True)[:n]
    
    # ==================== SUMMARY STATISTICS ====================
    
    def summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics.
        
        Returns:
            Dictionary with all key metrics including advanced statistics.
        """
        amounts = self.get_all_amounts()
        quartiles = self.quartiles()
        
        return {
            "total_transactions": self.count,
            "total_revenue": round(self.total_revenue(), 2),
            "total_quantity": self.total_quantity(),
            "average_transaction": round(self.average_transaction_value(), 2),
            "median_transaction": round(self.median_transaction_value(), 2),
            "std_deviation": round(self.std_deviation(), 2),
            "variance": round(self.variance(), 2),
            "coefficient_of_variation": round(self.coefficient_of_variation(), 2),
            "min_transaction": round(min(amounts), 2) if amounts else 0,
            "max_transaction": round(max(amounts), 2) if amounts else 0,
            "quartiles": {k: round(v, 2) for k, v in quartiles.items()},
            "unique_products": len(self.get_unique_products()),
            "unique_categories": len(self.get_unique_categories()),
            "unique_regions": len(self.get_unique_regions()),
            "unique_salespersons": len(self.get_unique_salespersons()),
            "revenue_by_category": {k: round(v, 2) for k, v in self.revenue_by_category().items()},
            "revenue_by_region": {k: round(v, 2) for k, v in self.revenue_by_region().items()},
        }

