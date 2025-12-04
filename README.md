# Intuit Build Challenge

Python implementations of two coding challenges demonstrating core programming competencies.

## Assignments

| # | Assignment | Key Concepts |
|---|------------|--------------|
| 1 | [Producer-Consumer Pattern](./assignment1_producer_consumer/) | Thread synchronization, Blocking queues, Wait/Notify |
| 2 | [CSV Data Analysis](./assignment2_data_analysis/) | Functional programming, map/filter/reduce, Lambda |

## Requirements

- **Python 3.8+** (uses standard library only, no external dependencies)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/parthhhx/intuit-build-challange.git
cd intuit-build-challange

# Run Assignment 1: Producer-Consumer
python3 run_assignment1.py

# Run Assignment 2: CSV Data Analysis
python3 run_assignment2.py
```

## Running Tests

```bash
# Assignment 1 Tests
python3 -m unittest assignment1_producer_consumer.tests.test_blocking_queue -v
python3 -m unittest assignment1_producer_consumer.tests.test_producer -v

# Assignment 2 Tests
python3 -m unittest assignment2_data_analysis.tests.test_models -v
python3 -m unittest assignment2_data_analysis.tests.test_analysis -v

# Run all tests
python3 -m unittest discover -v
```

## Project Structure

```
intuit-build-challange/
├── README.md                      # This file
├── requirements.txt               # Project dependencies
├── run_assignment1.py             # Runner for Assignment 1
├── run_assignment2.py             # Runner for Assignment 2
│
├── assignment1_producer_consumer/ # Assignment 1
│   ├── README.md
│   ├── requirements.txt
│   ├── blocking_queue.py          # Thread-safe bounded queue
│   ├── producer.py                # Producer thread
│   ├── consumer.py                # Consumer thread
│   ├── main.py                    # Demo scenarios
│   └── tests/
│       ├── test_blocking_queue.py
│       ├── test_producer.py
│       ├── test_consumer.py
│       └── test_integration.py
│
└── assignment2_data_analysis/     # Assignment 2
    ├── README.md
    ├── requirements.txt
    ├── models.py                  # SalesRecord dataclass
    ├── data_loader.py             # CSV loading functions
    ├── analysis.py                # SalesAnalyzer class
    ├── main.py                    # Demo scenarios
    ├── data/
    │   └── sales_data.csv         # Sample data (40 records)
    └── tests/
        ├── test_models.py
        ├── test_data_loader.py
        └── test_analysis.py
```

---

## Assignment 1: Producer-Consumer Pattern

Implements thread synchronization using `threading.Condition` for wait/notify mechanism.

### Features
- Thread-safe `BlockingQueue` with bounded capacity
- `Producer` reads from source, enqueues items
- `Consumer` dequeues items, stores in destination
- Statistics tracking and context manager support

### Sample Output
```
============================================================
Demo 1: Basic Producer-Consumer Pattern
============================================================
Source data: ['Item-0', 'Item-1', 'Item-2', ...]

  [Producer-1] Produced: Item-0
  [Consumer-1] Consumed: Item-0
  ...

All items transferred: True
```

---

## Assignment 2: CSV Data Analysis

Demonstrates functional programming with `map`, `filter`, `reduce`, and `lambda`.

### Features
- CSV data loading and parsing
- Aggregations: sum, average, min, max
- Filtering with lambda predicates
- Grouping by category, region, salesperson
- Rankings with sorted + lambda

### Sample Output
```
============================================================
  CSV DATA ANALYSIS WITH FUNCTIONAL PROGRAMMING
============================================================

Total Revenue: $33,516.13
Average Transaction: $837.90

Revenue by Category:
  Electronics: $23,138.72
  Furniture: $10,377.41

Top 5 Products by Revenue:
  1. Laptop Pro: $11,699.91
  2. Standing Desk: $3,599.94
  ...
```

---

## Author

Parth Chaudhari

## License

This project is submitted as part of the Intuit Build Challenge.
