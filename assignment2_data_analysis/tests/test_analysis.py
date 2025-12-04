"""
Unit tests for SalesAnalyzer class.

Tests functional programming operations: map, filter, reduce, lambda, groupby.
"""

import unittest
from datetime import date
from functools import reduce
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment2_data_analysis.models import SalesRecord
from assignment2_data_analysis.analysis import SalesAnalyzer


class TestAnalyzerSetup(unittest.TestCase):
    """Base class with test data setup."""
    
    def setUp(self):
        """Create test records."""
        self.records = [
            SalesRecord("TXN001", date(2024, 1, 15), "Laptop", "Electronics", 2, 1000.00, "North", "Alice"),
            SalesRecord("TXN002", date(2024, 1, 16), "Chair", "Furniture", 3, 200.00, "South", "Bob"),
            SalesRecord("TXN003", date(2024, 1, 17), "Mouse", "Electronics", 5, 30.00, "North", "Alice"),
            SalesRecord("TXN004", date(2024, 1, 18), "Desk", "Furniture", 1, 500.00, "East", "Carol"),
            SalesRecord("TXN005", date(2024, 1, 19), "Monitor", "Electronics", 2, 400.00, "South", "Bob"),
        ]
        self.analyzer = SalesAnalyzer(self.records)


class TestBasicAggregations(TestAnalyzerSetup):
    """Test basic aggregation operations using reduce."""
    
    def test_count(self):
        """Test record count."""
        self.assertEqual(self.analyzer.count, 5)
    
    def test_total_revenue(self):
        """Test total revenue calculation (uses reduce)."""
        # Manual calculation: 2000 + 600 + 150 + 500 + 800 = 4050
        expected = 2000.00 + 600.00 + 150.00 + 500.00 + 800.00
        self.assertAlmostEqual(self.analyzer.total_revenue(), expected, places=2)
    
    def test_total_quantity(self):
        """Test total quantity (uses sum + map)."""
        expected = 2 + 3 + 5 + 1 + 2
        self.assertEqual(self.analyzer.total_quantity(), expected)
    
    def test_average_transaction_value(self):
        """Test average calculation."""
        total = 2000.00 + 600.00 + 150.00 + 500.00 + 800.00
        expected = total / 5
        self.assertAlmostEqual(self.analyzer.average_transaction_value(), expected, places=2)
    
    def test_min_transaction(self):
        """Test finding minimum (uses min with lambda)."""
        min_record = self.analyzer.min_transaction()
        self.assertEqual(min_record.transaction_id, "TXN003")  # Mouse: $150
    
    def test_max_transaction(self):
        """Test finding maximum (uses max with lambda)."""
        max_record = self.analyzer.max_transaction()
        self.assertEqual(max_record.transaction_id, "TXN001")  # Laptop: $2000
    
    def test_empty_analyzer(self):
        """Test aggregations on empty data."""
        empty = SalesAnalyzer([])
        self.assertEqual(empty.total_revenue(), 0.0)
        self.assertEqual(empty.average_transaction_value(), 0.0)
        self.assertIsNone(empty.min_transaction())
        self.assertIsNone(empty.max_transaction())


class TestFilterOperations(TestAnalyzerSetup):
    """Test filter operations using filter() and lambda."""
    
    def test_filter_by_category(self):
        """Test filtering by category."""
        electronics = self.analyzer.filter_by_category("Electronics")
        self.assertEqual(electronics.count, 3)
        
        furniture = self.analyzer.filter_by_category("Furniture")
        self.assertEqual(furniture.count, 2)
    
    def test_filter_by_region(self):
        """Test filtering by region."""
        north = self.analyzer.filter_by_region("North")
        self.assertEqual(north.count, 2)
    
    def test_filter_by_salesperson(self):
        """Test filtering by salesperson."""
        alice = self.analyzer.filter_by_salesperson("Alice")
        self.assertEqual(alice.count, 2)
    
    def test_filter_by_min_amount(self):
        """Test filtering by minimum amount."""
        high_value = self.analyzer.filter_by_min_amount(500)
        self.assertEqual(high_value.count, 4)  # TXN001(2000), TXN002(600), TXN004(500), TXN005(800)
    
    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        filtered = self.analyzer.filter_by_date_range(
            date(2024, 1, 16),
            date(2024, 1, 18)
        )
        self.assertEqual(filtered.count, 3)
    
    def test_custom_filter(self):
        """Test custom predicate filter."""
        # Filter where quantity > 2
        result = self.analyzer.filter_by(lambda r: r.quantity > 2)
        self.assertEqual(result.count, 2)  # Chair (3) and Mouse (5)
    
    def test_chained_filters(self):
        """Test chaining multiple filters."""
        result = (self.analyzer
                  .filter_by_category("Electronics")
                  .filter_by_region("North"))
        self.assertEqual(result.count, 2)  # Laptop and Mouse
    
    def test_filter_returns_new_analyzer(self):
        """Test that filter returns new analyzer (immutable)."""
        original_count = self.analyzer.count
        filtered = self.analyzer.filter_by_category("Electronics")
        
        self.assertEqual(self.analyzer.count, original_count)
        self.assertNotEqual(filtered.count, original_count)


class TestGroupingOperations(TestAnalyzerSetup):
    """Test grouping operations."""
    
    def test_group_by_category(self):
        """Test grouping by category."""
        groups = self.analyzer.group_by_category()
        
        self.assertIn("Electronics", groups)
        self.assertIn("Furniture", groups)
        self.assertEqual(len(groups["Electronics"]), 3)
        self.assertEqual(len(groups["Furniture"]), 2)
    
    def test_group_by_region(self):
        """Test grouping by region."""
        groups = self.analyzer.group_by_region()
        
        self.assertEqual(len(groups["North"]), 2)
        self.assertEqual(len(groups["South"]), 2)
        self.assertEqual(len(groups["East"]), 1)
    
    def test_group_by_salesperson(self):
        """Test grouping by salesperson."""
        groups = self.analyzer.group_by_salesperson()
        
        self.assertEqual(len(groups["Alice"]), 2)
        self.assertEqual(len(groups["Bob"]), 2)
        self.assertEqual(len(groups["Carol"]), 1)
    
    def test_custom_group_by(self):
        """Test custom grouping function."""
        # Group by quantity range
        groups = self.analyzer.group_by(
            lambda r: "high" if r.quantity >= 3 else "low"
        )
        
        self.assertIn("high", groups)
        self.assertIn("low", groups)


class TestAggregationByGroup(TestAnalyzerSetup):
    """Test aggregations per group."""
    
    def test_revenue_by_category(self):
        """Test revenue aggregation by category (uses groupby + reduce)."""
        revenue = self.analyzer.revenue_by_category()
        
        # Electronics: 2000 + 150 + 800 = 2950
        self.assertAlmostEqual(revenue["Electronics"], 2950.00, places=2)
        # Furniture: 600 + 500 = 1100
        self.assertAlmostEqual(revenue["Furniture"], 1100.00, places=2)
    
    def test_revenue_by_region(self):
        """Test revenue by region."""
        revenue = self.analyzer.revenue_by_region()
        
        # North: 2000 + 150 = 2150
        self.assertAlmostEqual(revenue["North"], 2150.00, places=2)
    
    def test_quantity_by_product(self):
        """Test quantity aggregation by product."""
        qty = self.analyzer.quantity_by_product()
        
        self.assertEqual(qty["Laptop"], 2)
        self.assertEqual(qty["Mouse"], 5)
    
    def test_count_by_region(self):
        """Test transaction count by region."""
        counts = self.analyzer.count_by_region()
        
        self.assertEqual(counts["North"], 2)
        self.assertEqual(counts["South"], 2)
        self.assertEqual(counts["East"], 1)


class TestRankingOperations(TestAnalyzerSetup):
    """Test ranking operations using sorted with lambda."""
    
    def test_top_products_by_revenue(self):
        """Test top products ranking."""
        top = self.analyzer.top_products_by_revenue(3)
        
        self.assertEqual(len(top), 3)
        # Laptop should be first (2000)
        self.assertEqual(top[0][0], "Laptop")
    
    def test_top_salespersons(self):
        """Test top salespersons ranking."""
        top = self.analyzer.top_salespersons_by_revenue()
        
        # Alice: 2000 + 150 = 2150 (should be first)
        self.assertEqual(top[0][0], "Alice")
    
    def test_top_transactions(self):
        """Test top transactions by value."""
        top = self.analyzer.top_transactions(3)
        
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0].transaction_id, "TXN001")  # $2000


class TestTransformations(TestAnalyzerSetup):
    """Test transformation operations using map."""
    
    def test_get_all_amounts(self):
        """Test extracting all amounts (uses map)."""
        amounts = self.analyzer.get_all_amounts()
        
        self.assertEqual(len(amounts), 5)
        self.assertIn(2000.00, amounts)
    
    def test_get_unique_categories(self):
        """Test getting unique categories (uses set + map)."""
        categories = self.analyzer.get_unique_categories()
        
        self.assertEqual(len(categories), 2)
        self.assertIn("Electronics", categories)
        self.assertIn("Furniture", categories)
    
    def test_get_unique_regions(self):
        """Test getting unique regions."""
        regions = self.analyzer.get_unique_regions()
        
        self.assertEqual(len(regions), 3)  # North, South, East


class TestSummary(TestAnalyzerSetup):
    """Test summary statistics."""
    
    def test_summary_keys(self):
        """Test that summary contains all expected keys."""
        summary = self.analyzer.summary()
        
        expected_keys = [
            "total_transactions", "total_revenue", "total_quantity",
            "average_transaction", "min_transaction", "max_transaction",
            "unique_products", "unique_categories", "unique_regions",
            "unique_salespersons", "revenue_by_category", "revenue_by_region"
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
    
    def test_summary_values(self):
        """Test summary values are correct."""
        summary = self.analyzer.summary()
        
        self.assertEqual(summary["total_transactions"], 5)
        self.assertEqual(summary["unique_categories"], 2)


class TestAdvancedStatistics(TestAnalyzerSetup):
    """Test advanced statistical measures."""
    
    def test_median_odd_count(self):
        """Test median with odd number of records."""
        # 5 records: amounts are 2000, 600, 150, 500, 800
        # Sorted: 150, 500, 600, 800, 2000 -> median = 600
        median = self.analyzer.median_transaction_value()
        self.assertAlmostEqual(median, 600.00, places=2)
    
    def test_median_even_count(self):
        """Test median with even number of records."""
        # Add one more record
        records = self.records + [
            SalesRecord("TXN006", date(2024, 1, 20), "Tablet", "Electronics", 1, 300.00, "West", "David")
        ]
        analyzer = SalesAnalyzer(records)
        # Sorted amounts: 150, 300, 500, 600, 800, 2000 -> median = (500+600)/2 = 550
        median = analyzer.median_transaction_value()
        self.assertAlmostEqual(median, 550.00, places=2)
    
    def test_median_empty(self):
        """Test median with no records."""
        empty = SalesAnalyzer([])
        self.assertEqual(empty.median_transaction_value(), 0.0)
    
    def test_variance(self):
        """Test variance calculation."""
        variance = self.analyzer.variance()
        # Variance should be positive
        self.assertGreater(variance, 0)
    
    def test_std_deviation(self):
        """Test standard deviation calculation."""
        std_dev = self.analyzer.std_deviation()
        variance = self.analyzer.variance()
        # std_dev should be sqrt of variance
        import math
        self.assertAlmostEqual(std_dev, math.sqrt(variance), places=2)
    
    def test_percentile_bounds(self):
        """Test percentile at boundaries."""
        amounts = sorted([r.total_amount for r in self.records])
        
        # 0th percentile should be minimum
        p0 = self.analyzer.percentile(0)
        self.assertAlmostEqual(p0, min(amounts), places=2)
        
        # 100th percentile should be maximum
        p100 = self.analyzer.percentile(100)
        self.assertAlmostEqual(p100, max(amounts), places=2)
    
    def test_quartiles(self):
        """Test quartile calculation."""
        quartiles = self.analyzer.quartiles()
        
        self.assertIn("Q1", quartiles)
        self.assertIn("Q2", quartiles)
        self.assertIn("Q3", quartiles)
        self.assertIn("IQR", quartiles)
        
        # Q2 should equal median
        self.assertAlmostEqual(quartiles["Q2"], self.analyzer.median_transaction_value(), places=2)
        
        # IQR = Q3 - Q1
        self.assertAlmostEqual(quartiles["IQR"], quartiles["Q3"] - quartiles["Q1"], places=2)
    
    def test_coefficient_of_variation(self):
        """Test coefficient of variation."""
        cv = self.analyzer.coefficient_of_variation()
        mean = self.analyzer.average_transaction_value()
        std_dev = self.analyzer.std_deviation()
        
        expected = (std_dev / mean) * 100
        self.assertAlmostEqual(cv, expected, places=2)


class TestPartialFunctions(TestAnalyzerSetup):
    """Test partial function implementations."""
    
    def test_filter_by_category_partial(self):
        """Test partial-based category filter."""
        electronics = self.analyzer.filter_by_category_partial("Electronics")
        self.assertEqual(electronics.count, 3)
    
    def test_filter_by_region_partial(self):
        """Test partial-based region filter."""
        north = self.analyzer.filter_by_region_partial("North")
        self.assertEqual(north.count, 2)
    
    def test_filter_by_min_amount_partial(self):
        """Test partial-based amount filter."""
        high_value = self.analyzer.filter_by_min_amount_partial(500)
        self.assertEqual(high_value.count, 4)
    
    def test_partial_equals_lambda(self):
        """Test that partial filters give same results as lambda filters."""
        # Category filter
        lambda_result = self.analyzer.filter_by_category("Electronics")
        partial_result = self.analyzer.filter_by_category_partial("Electronics")
        self.assertEqual(lambda_result.count, partial_result.count)
        
        # Region filter
        lambda_result = self.analyzer.filter_by_region("North")
        partial_result = self.analyzer.filter_by_region_partial("North")
        self.assertEqual(lambda_result.count, partial_result.count)


if __name__ == '__main__':
    unittest.main()

