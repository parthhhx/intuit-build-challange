"""
Unit tests for SalesRecord model.
"""

import unittest
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment2_data_analysis.models import SalesRecord


class TestSalesRecord(unittest.TestCase):
    """Test SalesRecord dataclass."""
    
    def setUp(self):
        """Set up test data."""
        self.record = SalesRecord(
            transaction_id="TXN001",
            date=date(2024, 1, 15),
            product_name="Laptop",
            category="Electronics",
            quantity=2,
            unit_price=999.99,
            region="North",
            salesperson="Alice"
        )
    
    def test_creation(self):
        """Test record creation."""
        self.assertEqual(self.record.transaction_id, "TXN001")
        self.assertEqual(self.record.product_name, "Laptop")
        self.assertEqual(self.record.quantity, 2)
        self.assertEqual(self.record.unit_price, 999.99)
    
    def test_total_amount(self):
        """Test total_amount property."""
        expected = 2 * 999.99
        self.assertAlmostEqual(self.record.total_amount, expected, places=2)
    
    def test_from_dict(self):
        """Test creating record from dictionary."""
        data = {
            "transaction_id": "TXN002",
            "date": "2024-01-20",
            "product_name": "Mouse",
            "category": "Electronics",
            "quantity": "5",
            "unit_price": "29.99",
            "region": "South",
            "salesperson": "Bob"
        }
        record = SalesRecord.from_dict(data)
        
        self.assertEqual(record.transaction_id, "TXN002")
        self.assertEqual(record.date, date(2024, 1, 20))
        self.assertEqual(record.quantity, 5)
        self.assertEqual(record.unit_price, 29.99)
    
    def test_to_dict(self):
        """Test converting record to dictionary."""
        result = self.record.to_dict()
        
        self.assertEqual(result["transaction_id"], "TXN001")
        self.assertEqual(result["date"], "2024-01-15")
        self.assertEqual(result["quantity"], 2)
        self.assertIn("total_amount", result)
    
    def test_immutability(self):
        """Test that record is immutable (frozen dataclass)."""
        with self.assertRaises(AttributeError):
            self.record.quantity = 10
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.record)
        self.assertIn("TXN001", repr_str)
        self.assertIn("Laptop", repr_str)


if __name__ == '__main__':
    unittest.main()

