"""
CSV Data Analysis Demo

Demonstrates functional programming operations on sales data:
- map, filter, reduce
- Lambda expressions  
- Data aggregation and grouping
"""

import os
from pathlib import Path
from datetime import date
from .data_loader import load_sales_data
from .analysis import SalesAnalyzer


def get_data_path() -> str:
    """Get path to the sales data CSV file."""
    current_dir = Path(__file__).parent
    return str(current_dir / "data" / "sales_data.csv")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_basic_loading():
    """Demonstrate loading CSV data."""
    print_section("1. Loading CSV Data")
    
    data_path = get_data_path()
    records = load_sales_data(data_path)
    
    print(f"Loaded {len(records)} sales records from CSV")
    print(f"\nFirst 3 records:")
    for record in records[:3]:
        print(f"  {record}")


def demo_basic_aggregations(analyzer: SalesAnalyzer):
    """Demonstrate basic aggregation operations."""
    print_section("2. Basic Aggregations (using reduce & map)")
    
    print(f"Total Transactions: {analyzer.count}")
    print(f"Total Revenue: ${analyzer.total_revenue():,.2f}")
    print(f"Total Quantity Sold: {analyzer.total_quantity():,}")
    print(f"Average Transaction Value: ${analyzer.average_transaction_value():.2f}")
    
    min_txn = analyzer.min_transaction()
    max_txn = analyzer.max_transaction()
    print(f"\nSmallest Transaction: {min_txn.transaction_id} - ${min_txn.total_amount:.2f}")
    print(f"Largest Transaction: {max_txn.transaction_id} - ${max_txn.total_amount:.2f}")


def demo_filtering(analyzer: SalesAnalyzer):
    """Demonstrate filter operations with lambda."""
    print_section("3. Filtering (using filter & lambda)")
    
    # Filter by category
    electronics = analyzer.filter_by_category("Electronics")
    print(f"\nElectronics Sales:")
    print(f"  Transactions: {electronics.count}")
    print(f"  Revenue: ${electronics.total_revenue():,.2f}")
    
    furniture = analyzer.filter_by_category("Furniture")
    print(f"\nFurniture Sales:")
    print(f"  Transactions: {furniture.count}")
    print(f"  Revenue: ${furniture.total_revenue():,.2f}")
    
    # Filter by region
    print(f"\nSales by Region (filtered):")
    for region in ["North", "South", "East", "West"]:
        regional = analyzer.filter_by_region(region)
        print(f"  {region}: {regional.count} transactions, ${regional.total_revenue():,.2f}")
    
    # Filter by minimum amount
    high_value = analyzer.filter_by_min_amount(500)
    print(f"\nHigh-Value Transactions (>= $500): {high_value.count}")
    
    # Chained filters
    north_electronics = analyzer.filter_by_region("North").filter_by_category("Electronics")
    print(f"\nNorth Region + Electronics: {north_electronics.count} transactions")


def demo_grouping(analyzer: SalesAnalyzer):
    """Demonstrate grouping operations."""
    print_section("4. Grouping Operations (using groupby)")
    
    print("\nRevenue by Category:")
    for category, revenue in sorted(analyzer.revenue_by_category().items()):
        print(f"  {category}: ${revenue:,.2f}")
    
    print("\nRevenue by Region:")
    for region, revenue in sorted(analyzer.revenue_by_region().items()):
        print(f"  {region}: ${revenue:,.2f}")
    
    print("\nTransactions by Region:")
    for region, count in sorted(analyzer.count_by_region().items()):
        print(f"  {region}: {count} transactions")
    
    print("\nQuantity Sold by Product:")
    qty_by_product = analyzer.quantity_by_product()
    for product, qty in sorted(qty_by_product.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {product}: {qty} units")


def demo_ranking(analyzer: SalesAnalyzer):
    """Demonstrate ranking operations."""
    print_section("5. Rankings (using sorted with lambda)")
    
    print("\nTop 5 Products by Revenue:")
    for i, (product, revenue) in enumerate(analyzer.top_products_by_revenue(5), 1):
        print(f"  {i}. {product}: ${revenue:,.2f}")
    
    print("\nTop Salespersons by Revenue:")
    for i, (person, revenue) in enumerate(analyzer.top_salespersons_by_revenue(), 1):
        print(f"  {i}. {person}: ${revenue:,.2f}")
    
    print("\nTop 5 Transactions by Value:")
    for i, record in enumerate(analyzer.top_transactions(5), 1):
        print(f"  {i}. {record.transaction_id}: {record.product_name} - ${record.total_amount:,.2f}")


def demo_functional_patterns(analyzer: SalesAnalyzer):
    """Demonstrate explicit functional programming patterns."""
    print_section("6. Functional Programming Patterns")
    
    records = analyzer.records
    
    # MAP: Transform records to amounts
    print("\nMAP - Extract all transaction amounts:")
    amounts = list(map(lambda r: r.total_amount, records[:5]))
    print(f"  First 5 amounts: {[f'${a:.2f}' for a in amounts]}")
    
    # FILTER: High-value transactions
    print("\nFILTER - Transactions over $1000:")
    high_value = list(filter(lambda r: r.total_amount > 1000, records))
    print(f"  Found {len(high_value)} transactions")
    for r in high_value[:3]:
        print(f"    {r.transaction_id}: ${r.total_amount:.2f}")
    
    # REDUCE: Calculate total
    from functools import reduce
    print("\nREDUCE - Sum all quantities:")
    total_qty = reduce(lambda acc, r: acc + r.quantity, records, 0)
    print(f"  Total quantity: {total_qty}")
    
    # Combined: Filter -> Map -> Reduce
    print("\nCOMBINED (filter -> map -> reduce):")
    print("  Electronics total revenue:")
    electronics_revenue = reduce(
        lambda acc, amount: acc + amount,
        map(
            lambda r: r.total_amount,
            filter(lambda r: r.category == "Electronics", records)
        ),
        0.0
    )
    print(f"  ${electronics_revenue:,.2f}")
    
    # Lambda with sorting
    print("\nSORTED with lambda key:")
    print("  Top 3 by quantity (single transaction):")
    by_quantity = sorted(records, key=lambda r: r.quantity, reverse=True)[:3]
    for r in by_quantity:
        print(f"    {r.product_name}: {r.quantity} units")


def demo_partial_functions(analyzer: SalesAnalyzer):
    """Demonstrate functools.partial usage."""
    print_section("7. Partial Functions (functools.partial)")
    
    from assignment2_data_analysis.analysis import (
        get_amount, get_quantity, get_category,
        make_category_filter, make_region_filter, make_min_amount_filter
    )
    
    records = analyzer.records
    
    # Using partial functions to extract attributes
    print("\nUsing partial functions for attribute extraction:")
    print(f"  get_amount(record) = partial(_get_attribute, 'total_amount')")
    amounts = list(map(get_amount, records[:3]))
    print(f"  First 3 amounts: {[f'${a:.2f}' for a in amounts]}")
    
    quantities = list(map(get_quantity, records[:3]))
    print(f"  First 3 quantities: {quantities}")
    
    # Using partial filter factories
    print("\nUsing partial function factories for filtering:")
    
    # Create reusable filters
    electronics_filter = make_category_filter("Electronics")
    north_filter = make_region_filter("North")
    high_value_filter = make_min_amount_filter(1000)
    
    print("  electronics_filter = make_category_filter('Electronics')")
    electronics = list(filter(electronics_filter, records))
    print(f"  Electronics transactions: {len(electronics)}")
    
    print("  high_value_filter = make_min_amount_filter(1000)")
    high_value = list(filter(high_value_filter, records))
    print(f"  High-value (>=$1000) transactions: {len(high_value)}")
    
    # Using analyzer's partial-based methods
    print("\nUsing analyzer's partial-based filter methods:")
    north_electronics = (analyzer
        .filter_by_region_partial("North")
        .filter_by_category_partial("Electronics"))
    print(f"  North + Electronics (via partial): {north_electronics.count} transactions")


def demo_advanced_statistics(analyzer: SalesAnalyzer):
    """Demonstrate advanced statistical measures."""
    print_section("8. Advanced Statistics (median, std dev, percentiles)")
    
    print("\nCentral Tendency:")
    print(f"  Mean (Average):  ${analyzer.average_transaction_value():,.2f}")
    print(f"  Median:          ${analyzer.median_transaction_value():,.2f}")
    
    print("\nDispersion Measures:")
    print(f"  Variance:        ${analyzer.variance():,.2f}")
    print(f"  Std Deviation:   ${analyzer.std_deviation():,.2f}")
    print(f"  CV (volatility): {analyzer.coefficient_of_variation():.2f}%")
    
    print("\nQuartiles:")
    quartiles = analyzer.quartiles()
    print(f"  Q1 (25th percentile): ${quartiles['Q1']:,.2f}")
    print(f"  Q2 (50th/Median):     ${quartiles['Q2']:,.2f}")
    print(f"  Q3 (75th percentile): ${quartiles['Q3']:,.2f}")
    print(f"  IQR (Q3-Q1):          ${quartiles['IQR']:,.2f}")
    
    print("\nCustom Percentiles:")
    print(f"  10th percentile: ${analyzer.percentile(10):,.2f}")
    print(f"  90th percentile: ${analyzer.percentile(90):,.2f}")


def demo_summary(analyzer: SalesAnalyzer):
    """Display comprehensive summary."""
    print_section("9. Summary Statistics")
    
    summary = analyzer.summary()
    
    print(f"\n{'Metric':<30} {'Value':>20}")
    print("-" * 52)
    print(f"{'Total Transactions':<30} {summary['total_transactions']:>20,}")
    print(f"{'Total Revenue':<30} ${summary['total_revenue']:>19,.2f}")
    print(f"{'Total Quantity':<30} {summary['total_quantity']:>20,}")
    print(f"{'Average Transaction':<30} ${summary['average_transaction']:>19,.2f}")
    print(f"{'Median Transaction':<30} ${summary['median_transaction']:>19,.2f}")
    print(f"{'Std Deviation':<30} ${summary['std_deviation']:>19,.2f}")
    print(f"{'Min Transaction':<30} ${summary['min_transaction']:>19,.2f}")
    print(f"{'Max Transaction':<30} ${summary['max_transaction']:>19,.2f}")
    print(f"{'Unique Products':<30} {summary['unique_products']:>20}")
    print(f"{'Unique Categories':<30} {summary['unique_categories']:>20}")
    print(f"{'Unique Regions':<30} {summary['unique_regions']:>20}")
    print(f"{'Unique Salespersons':<30} {summary['unique_salespersons']:>20}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("  CSV DATA ANALYSIS WITH FUNCTIONAL PROGRAMMING")
    print("  map | filter | reduce | lambda | partial | groupby")
    print("=" * 60)
    
    # Load data
    data_path = get_data_path()
    records = load_sales_data(data_path)
    analyzer = SalesAnalyzer(records)
    
    # Run demos
    demo_basic_loading()
    demo_basic_aggregations(analyzer)
    demo_filtering(analyzer)
    demo_grouping(analyzer)
    demo_ranking(analyzer)
    demo_functional_patterns(analyzer)
    demo_partial_functions(analyzer)
    demo_advanced_statistics(analyzer)
    demo_summary(analyzer)
    
    print("\n" + "=" * 60)
    print("  Analysis completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

