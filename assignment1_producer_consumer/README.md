# Assignment 1: Producer-Consumer Pattern

A thread-safe implementation of the classic producer-consumer pattern using Python's `threading` module.

## Features

- **BlockingQueue**: Bounded buffer with `threading.Condition` for wait/notify synchronization
- **Producer**: Reads from any iterable source and enqueues items
- **Consumer**: Dequeues items and stores in a destination container
- **Thread-safe**: Proper synchronization prevents race conditions

## Project Structure

```
assignment1_producer_consumer/
├── blocking_queue.py    # Thread-safe bounded queue
├── producer.py          # Producer thread implementation
├── consumer.py          # Consumer thread implementation
├── main.py              # Demo scenarios
└── tests/               # Unit tests
```

## Quick Start

```bash
# Run demo
python3 run_assignment1.py

# Run tests
python3 -m unittest assignment1_producer_consumer.tests.test_blocking_queue -v
python3 -m unittest assignment1_producer_consumer.tests.test_producer -v
```

## Usage Example

```python
from assignment1_producer_consumer import BlockingQueue, Producer, Consumer

# Create shared queue (capacity=5)
queue = BlockingQueue(capacity=5)

# Source and destination
source = ["item1", "item2", "item3"]
destination = []

# Create and start threads
producer = Producer(queue=queue, source=source)
consumer = Consumer(queue=queue, destination=destination, timeout=1.0)

consumer.start()
producer.start()

producer.join()
queue.shutdown()  # Signal consumer to stop
consumer.join()

print(destination)  # ['item1', 'item2', 'item3']
```

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Thread Synchronization | `threading.Condition` with `wait()`/`notify()` |
| Blocking Queue | Bounded buffer that blocks on full/empty |
| Graceful Shutdown | `shutdown()` method releases all waiting threads |
| Thread Safety | All shared state protected by locks |
| Context Manager | Auto-cleanup with `with` statement |
| Statistics Tracking | Monitor blocked puts/gets, throughput |

## Sample Output

```
============================================================
Demo 1: Basic Producer-Consumer Pattern
============================================================
Source data: ['Item-0', 'Item-1', 'Item-2', ...]

Starting producer and consumer...
  [Producer-1] Produced: Item-0
  [Consumer-1] Consumed: Item-0
  [Producer-1] Produced: Item-1
  [Consumer-1] Consumed: Item-1
  ...

Producer finished. Items produced: 10
Consumer finished. Items consumed: 10
All items transferred: True
```

## Assumptions

The following assumptions were made during implementation:

| # | Assumption | Rationale |
|---|------------|-----------|
| 1 | **Bounded Queue Capacity** | Queue has a fixed maximum capacity (default 10). This prevents unbounded memory growth and demonstrates blocking behavior when full. |
| 2 | **FIFO Order** | Items are processed in First-In-First-Out order. With a single producer and single consumer, order is preserved. With multiple consumers, global order is not guaranteed. |
| 3 | **Graceful Shutdown** | System shuts down gracefully via `queue.shutdown()`. Producer completes current item, consumers drain remaining items before stopping. |
| 4 | **No Item Processing Errors** | Items are assumed to be valid and processing won't throw exceptions. Error handling during production/consumption is left to the callback functions. |
| 5 | **Generic Item Types** | Queue accepts any Python object (`Any` type). No type validation is performed on items. |
| 6 | **Blocking with Timeout** | Operations can block indefinitely (`timeout=None`) or with a specified timeout. Callers must handle timeout scenarios. |
| 7 | **Single Source per Producer** | Each producer reads from one iterable source. Source is exhausted sequentially; producer stops when source is empty. |
| 8 | **Thread-Safe Destination** | When using multiple consumers, a thread-safe `DestinationContainer` should be used. Single consumer can use a regular list. |
| 9 | **No Priority Queue** | All items have equal priority. No support for priority-based dequeuing. |
| 10 | **In-Memory Only** | Queue and data are held in memory. No persistence or recovery mechanism for system failures. |

## API Reference

### BlockingQueue(capacity=10)
- `put(item, timeout=None)` → `bool` - Add item, blocks if full
- `get(timeout=None)` → `(bool, item)` - Remove item, blocks if empty
- `shutdown()` - Release all waiting threads
- `size()`, `is_empty()`, `is_full()`
- `get_statistics()` → `dict` - Get throughput & blocking stats
- Supports context manager: `with BlockingQueue() as q:`

### Producer(queue, source, name="Producer", delay=0, on_produce=None)
- Extends `threading.Thread`
- `items_produced` - Count of items produced
- `stop()` - Signal to stop

### Consumer(queue, destination=None, name="Consumer", delay=0, on_consume=None, timeout=1.0)
- Extends `threading.Thread`
- `items_consumed` - Count of items consumed
- `destination` - List of consumed items
- `stop()` - Signal to stop

