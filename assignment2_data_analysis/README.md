# Assignment 2: CSV Data Analysis with Functional Programming

Demonstrates proficiency with functional programming by performing aggregation and grouping operations on sales data.

## Features

- **Data Loading**: CSV parsing with `csv.DictReader` and `map()`
- **Aggregations**: sum, average, min, max using `reduce()`
- **Filtering**: `filter()` with lambda predicates
- **Grouping**: Group by category, region, salesperson
- **Transformations**: `map()` for data extraction
- **Rankings**: `sorted()` with lambda key functions

## Project Structure

```
assignment2_data_analysis/
├── models.py          # SalesRecord dataclass
├── data_loader.py     # CSV loading functions
├── analysis.py        # SalesAnalyzer with functional operations
├── main.py            # Demo scenarios
├── data/
│   └── sales_data.csv # Sample sales data (40 transactions)
└── tests/             # Unit tests
```

## Quick Start

```bash
# Run demo
python3 run_assignment2.py

# Run tests
python3 -m unittest assignment2_data_analysis.tests.test_analysis -v
```

## Usage Example

```python
from assignment2_data_analysis import load_sales_data, SalesAnalyzer

# Load data
records = load_sales_data("path/to/sales.csv")
analyzer = SalesAnalyzer(records)

# Aggregations (uses reduce)
print(f"Total Revenue: ${analyzer.total_revenue():,.2f}")
print(f"Average Transaction: ${analyzer.average_transaction_value():.2f}")

# Filtering (uses filter + lambda)
electronics = analyzer.filter_by_category("Electronics")
high_value = analyzer.filter_by_min_amount(500)

# Grouping + aggregation
revenue_by_region = analyzer.revenue_by_region()
top_products = analyzer.top_products_by_revenue(5)

# Chained operations
north_electronics = (analyzer
    .filter_by_region("North")
    .filter_by_category("Electronics"))
```

## Functional Programming Patterns Used

| Pattern | Example |
|---------|---------|
| `map()` | `map(lambda r: r.total_amount, records)` |
| `filter()` | `filter(lambda r: r.category == "Electronics", records)` |
| `reduce()` | `reduce(lambda acc, r: acc + r.total_amount, records, 0)` |
| Lambda | `key=lambda r: r.total_amount` |
| `partial()` | `get_amount = partial(_get_attribute, 'total_amount')` |
| Chained | `filter -> map -> reduce` pipeline |

## Advanced Features

### Partial Functions (functools.partial)

```python
from assignment2_data_analysis.analysis import (
    get_amount, make_category_filter, make_min_amount_filter
)

# Pre-built partial functions for attribute extraction
amounts = list(map(get_amount, records))

# Partial function factories for reusable filters
electronics_filter = make_category_filter("Electronics")
high_value_filter = make_min_amount_filter(1000)

filtered = list(filter(electronics_filter, records))
```

### Advanced Statistics

```python
analyzer.median_transaction_value()   # Median
analyzer.std_deviation()              # Standard deviation
analyzer.variance()                   # Variance
analyzer.percentile(75)               # Any percentile
analyzer.quartiles()                  # Q1, Q2, Q3, IQR
analyzer.coefficient_of_variation()   # CV (volatility)
```

## Sample Output

```
============================================================
  CSV DATA ANALYSIS WITH FUNCTIONAL PROGRAMMING
============================================================

2. Basic Aggregations (using reduce & map)
Total Transactions: 40
Total Revenue: $38,847.12
Average Transaction Value: $971.18

3. Filtering (using filter & lambda)
Electronics Sales:
  Transactions: 24
  Revenue: $28,858.32

4. Grouping Operations (using groupby)
Revenue by Category:
  Electronics: $28,858.32
  Furniture: $9,988.80

5. Rankings (using sorted with lambda)
Top 5 Products by Revenue:
  1. Laptop Pro: $11,699.91
  2. Standing Desk: $3,599.94
  ...
```

## Assumptions

The following assumptions were made during implementation:

| # | Assumption | Rationale |
|---|------------|-----------|
| 1 | **CSV Column Structure** | CSV files must have specific headers: `transaction_id`, `date`, `product_name`, `category`, `quantity`, `unit_price`, `region`, `salesperson`. |
| 2 | **Date Format** | Dates are in ISO format (`YYYY-MM-DD`). Other formats will cause parsing errors. |
| 3 | **Data Types** | `quantity` is a positive integer, `unit_price` is a positive float. No validation is performed on negative values. |
| 4 | **No Missing Values** | All CSV fields are present and non-empty. Missing values will cause errors during parsing. |
| 5 | **Single Currency** | All prices are assumed to be in the same currency (USD). No currency conversion is performed. |
| 6 | **Case-Sensitive Matching** | String comparisons (category, region, salesperson) are case-sensitive. "Electronics" ≠ "electronics". |
| 7 | **In-Memory Processing** | All data is loaded into memory. Not suitable for very large datasets (millions of records). |
| 8 | **Immutable Records** | `SalesRecord` is a frozen dataclass. Records cannot be modified after creation. |
| 9 | **UTF-8 Encoding** | CSV files are assumed to be UTF-8 encoded. Other encodings may cause issues. |
| 10 | **No Duplicate Transactions** | Each `transaction_id` is unique. Duplicates are not detected or handled. |
| 11 | **Positive Quantities** | Quantities represent sales, not returns. Negative quantities are not handled specially. |
| 12 | **Functional Purity** | Filter operations return new `SalesAnalyzer` instances (immutable pattern). Original data is never modified. |

## API Reference

### SalesAnalyzer(records)

**Aggregations:**
- `total_revenue()` → `float`
- `total_quantity()` → `int`
- `average_transaction_value()` → `float`
- `min_transaction()` / `max_transaction()` → `SalesRecord`

**Advanced Statistics:**
- `median_transaction_value()` → `float`
- `std_deviation()` → `float`
- `variance()` → `float`
- `percentile(p)` → `float` (0-100)
- `quartiles()` → `Dict` (Q1, Q2, Q3, IQR)
- `coefficient_of_variation()` → `float`

**Filtering (lambda-based):**
- `filter_by(predicate)` → `SalesAnalyzer`
- `filter_by_category(category)` → `SalesAnalyzer`
- `filter_by_region(region)` → `SalesAnalyzer`
- `filter_by_min_amount(amount)` → `SalesAnalyzer`

**Filtering (partial-based):**
- `filter_by_category_partial(category)` → `SalesAnalyzer`
- `filter_by_region_partial(region)` → `SalesAnalyzer`
- `filter_by_min_amount_partial(amount)` → `SalesAnalyzer`

**Grouping:**
- `group_by_category()` → `Dict[str, List[SalesRecord]]`
- `revenue_by_category()` → `Dict[str, float]`
- `revenue_by_region()` → `Dict[str, float]`

**Rankings:**
- `top_products_by_revenue(n)` → `List[Tuple[str, float]]`
- `top_salespersons_by_revenue(n)` → `List[Tuple[str, float]]`

