"""
Data Models for Sales Analysis

Defines the SalesRecord dataclass representing a single sales transaction.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class SalesRecord:
    """
    Represents a single sales transaction record.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        date: Date of the transaction
        product_name: Name of the product sold
        category: Product category (e.g., Electronics, Furniture)
        quantity: Number of units sold
        unit_price: Price per unit
        region: Sales region (e.g., North, South, East, West)
        salesperson: Name of the salesperson
    """
    transaction_id: str
    date: date
    product_name: str
    category: str
    quantity: int
    unit_price: float
    region: str
    salesperson: str
    
    @property
    def total_amount(self) -> float:
        """Calculate total amount for this transaction."""
        return self.quantity * self.unit_price
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SalesRecord':
        """
        Create a SalesRecord from a dictionary.
        
        Args:
            data: Dictionary with keys matching field names.
                  Date should be in 'YYYY-MM-DD' format.
        
        Returns:
            A new SalesRecord instance.
        """
        return cls(
            transaction_id=data['transaction_id'],
            date=date.fromisoformat(data['date']),
            product_name=data['product_name'],
            category=data['category'],
            quantity=int(data['quantity']),
            unit_price=float(data['unit_price']),
            region=data['region'],
            salesperson=data['salesperson']
        )
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'date': self.date.isoformat(),
            'product_name': self.product_name,
            'category': self.category,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'region': self.region,
            'salesperson': self.salesperson,
            'total_amount': self.total_amount
        }
    
    def __repr__(self) -> str:
        return (f"SalesRecord({self.transaction_id}, {self.date}, "
                f"{self.product_name}, ${self.total_amount:.2f})")

