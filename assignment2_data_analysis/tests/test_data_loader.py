"""
Unit tests for data loading functions.
"""

import unittest
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment2_data_analysis.data_loader import load_sales_from_string, load_sales_data
from assignment2_data_analysis.models import SalesRecord


class TestDataLoader(unittest.TestCase):
    """Test CSV loading functions."""
    
    def setUp(self):
        """Set up test CSV data."""
        self.csv_content = """transaction_id,date,product_name,category,quantity,unit_price,region,salesperson
TXN001,2024-01-15,Laptop,Electronics,2,999.99,North,Alice
TXN002,2024-01-16,Chair,Furniture,3,199.99,South,Bob
TXN003,2024-01-17,Mouse,Electronics,5,29.99,East,Carol"""
    
    def test_load_from_string(self):
        """Test loading data from CSV string."""
        records = load_sales_from_string(self.csv_content)
        
        self.assertEqual(len(records), 3)
        self.assertIsInstance(records[0], SalesRecord)
    
    def test_record_values(self):
        """Test that loaded records have correct values."""
        records = load_sales_from_string(self.csv_content)
        
        first = records[0]
        self.assertEqual(first.transaction_id, "TXN001")
        self.assertEqual(first.product_name, "Laptop")
        self.assertEqual(first.quantity, 2)
        self.assertEqual(first.unit_price, 999.99)
        self.assertEqual(first.date, date(2024, 1, 15))
    
    def test_load_preserves_order(self):
        """Test that records are loaded in order."""
        records = load_sales_from_string(self.csv_content)
        
        ids = [r.transaction_id for r in records]
        self.assertEqual(ids, ["TXN001", "TXN002", "TXN003"])
    
    def test_empty_csv(self):
        """Test loading empty CSV (header only)."""
        csv_content = "transaction_id,date,product_name,category,quantity,unit_price,region,salesperson"
        records = load_sales_from_string(csv_content)
        
        self.assertEqual(len(records), 0)
    
    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with self.assertRaises(FileNotFoundError):
            load_sales_data("/nonexistent/path/data.csv")


class TestFunctionalLoading(unittest.TestCase):
    """Test functional aspects of data loading."""
    
    def setUp(self):
        """Set up test data."""
        self.csv_content = """transaction_id,date,product_name,category,quantity,unit_price,region,salesperson
TXN001,2024-01-15,Laptop,Electronics,2,999.99,North,Alice
TXN002,2024-01-16,Chair,Furniture,3,199.99,South,Bob
TXN003,2024-01-17,Mouse,Electronics,5,29.99,East,Carol
TXN004,2024-01-18,Desk,Furniture,1,499.99,West,David"""
    
    def test_map_transformation(self):
        """Test using map on loaded data."""
        records = load_sales_from_string(self.csv_content)
        
        # Map to extract amounts
        amounts = list(map(lambda r: r.total_amount, records))
        
        self.assertEqual(len(amounts), 4)
        self.assertAlmostEqual(amounts[0], 1999.98, places=2)
    
    def test_filter_transformation(self):
        """Test using filter on loaded data."""
        records = load_sales_from_string(self.csv_content)
        
        # Filter electronics only
        electronics = list(filter(lambda r: r.category == "Electronics", records))
        
        self.assertEqual(len(electronics), 2)
        self.assertTrue(all(r.category == "Electronics" for r in electronics))


if __name__ == '__main__':
    unittest.main()

