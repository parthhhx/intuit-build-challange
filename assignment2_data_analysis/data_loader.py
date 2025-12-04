"""
CSV Data Loader

Functions for loading and parsing sales data from CSV files.
Uses functional programming patterns for data transformation.
"""

import csv
from typing import List, Iterator, Callable
from pathlib import Path
from .models import SalesRecord


def load_sales_data(filepath: str) -> List[SalesRecord]:
    """
    Load sales data from a CSV file.
    
    Uses functional approach with map() to transform CSV rows to SalesRecord objects.
    
    Args:
        filepath: Path to the CSV file.
    
    Returns:
        List of SalesRecord objects.
    
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the CSV format is invalid.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    with open(path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Functional: map each row dict to a SalesRecord
        records = list(map(SalesRecord.from_dict, reader))
    
    return records


def load_sales_from_string(csv_content: str) -> List[SalesRecord]:
    """
    Load sales data from a CSV string.
    
    Useful for testing without file I/O.
    
    Args:
        csv_content: CSV content as a string.
    
    Returns:
        List of SalesRecord objects.
    """
    import io
    reader = csv.DictReader(io.StringIO(csv_content))
    return list(map(SalesRecord.from_dict, reader))


def stream_sales_data(filepath: str) -> Iterator[SalesRecord]:
    """
    Stream sales data from CSV file (memory-efficient for large files).
    
    Yields one record at a time using a generator pattern.
    
    Args:
        filepath: Path to the CSV file.
    
    Yields:
        SalesRecord objects one at a time.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    with open(path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield SalesRecord.from_dict(row)


def filter_and_load(
    filepath: str,
    predicate: Callable[[SalesRecord], bool]
) -> List[SalesRecord]:
    """
    Load and filter sales data in one pass.
    
    Combines streaming with filtering for efficient memory usage.
    
    Args:
        filepath: Path to the CSV file.
        predicate: Function that returns True for records to include.
    
    Returns:
        List of filtered SalesRecord objects.
    """
    return list(filter(predicate, stream_sales_data(filepath)))

