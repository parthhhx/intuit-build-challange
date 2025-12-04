"""
Producer-Consumer Pattern Demo

This module demonstrates the producer-consumer pattern with thread
synchronization using a blocking queue.
"""

import time
from typing import List
from .blocking_queue import BlockingQueue
from .producer import Producer, ItemGenerator
from .consumer import Consumer, DestinationContainer


def demo_basic_producer_consumer():
    """
    Demonstrate basic producer-consumer pattern.
    
    A single producer creates items and a single consumer processes them.
    """
    print("=" * 60)
    print("Demo 1: Basic Producer-Consumer Pattern")
    print("=" * 60)
    
    # Create shared blocking queue with capacity of 5
    queue = BlockingQueue(capacity=5)
    
    # Source data
    source_data = [f"Item-{i}" for i in range(10)]
    print(f"Source data: {source_data}")
    
    # Destination container
    destination: List[str] = []
    
    # Create producer and consumer
    producer = Producer(
        queue=queue,
        source=source_data,
        name="Producer-1",
        on_produce=lambda item: print(f"  [Producer-1] Produced: {item}")
    )
    
    consumer = Consumer(
        queue=queue,
        destination=destination,
        name="Consumer-1",
        on_consume=lambda item: print(f"  [Consumer-1] Consumed: {item}")
    )
    
    # Start both threads
    print("\nStarting producer and consumer...")
    consumer.start()
    producer.start()
    
    # Wait for producer to finish
    producer.join()
    print(f"\nProducer finished. Items produced: {producer.items_produced}")
    
    # Shutdown queue to signal consumer
    queue.shutdown()
    
    # Wait for consumer to finish
    consumer.join()
    print(f"Consumer finished. Items consumed: {consumer.items_consumed}")
    
    # Verify results
    print(f"\nDestination data: {destination}")
    print(f"All items transferred: {source_data == destination}")


def demo_multiple_producers_consumers():
    """
    Demonstrate multiple producers and consumers.
    
    Multiple producers add items to the queue and multiple consumers
    process them concurrently.
    """
    print("\n" + "=" * 60)
    print("Demo 2: Multiple Producers and Consumers")
    print("=" * 60)
    
    # Create shared blocking queue with capacity of 3
    queue = BlockingQueue(capacity=3)
    
    # Thread-safe destination container
    destination = DestinationContainer()
    
    # Create multiple producers with different sources
    producers = [
        Producer(
            queue=queue,
            source=[f"P{i}-Item-{j}" for j in range(5)],
            name=f"Producer-{i}",
            delay=0.01,
            on_produce=lambda item, name=f"Producer-{i}": print(f"  [{name}] Produced: {item}")
        )
        for i in range(2)
    ]
    
    # Create multiple consumers
    consumers = [
        Consumer(
            queue=queue,
            destination=destination,
            name=f"Consumer-{i}",
            delay=0.02,
            on_consume=lambda item, name=f"Consumer-{i}": print(f"  [{name}] Consumed: {item}")
        )
        for i in range(3)
    ]
    
    print(f"\nStarting {len(producers)} producers and {len(consumers)} consumers...")
    
    # Start all threads
    for consumer in consumers:
        consumer.start()
    for producer in producers:
        producer.start()
    
    # Wait for all producers to finish
    for producer in producers:
        producer.join()
    
    print(f"\nAll producers finished.")
    
    # Shutdown queue
    queue.shutdown()
    
    # Wait for all consumers to finish
    for consumer in consumers:
        consumer.join()
    
    print(f"All consumers finished.")
    
    # Results
    total_produced = sum(p.items_produced for p in producers)
    total_consumed = sum(c.items_consumed for c in consumers)
    
    print(f"\nTotal items produced: {total_produced}")
    print(f"Total items consumed: {total_consumed}")
    print(f"Items in destination: {destination.size()}")
    print(f"All items accounted for: {total_produced == total_consumed == destination.size()}")


def demo_with_item_generator():
    """
    Demonstrate using an item generator as the source.
    """
    print("\n" + "=" * 60)
    print("Demo 3: Using Item Generator")
    print("=" * 60)
    
    # Create shared queue
    queue = BlockingQueue(capacity=5)
    
    # Create an item generator that generates custom objects
    def generate_task(index: int) -> dict:
        return {
            "id": index,
            "task": f"Process data batch {index}",
            "priority": index % 3
        }
    
    source = ItemGenerator(count=8, generator_func=generate_task)
    print(f"Generating {len(source)} task items...")
    
    # Destination
    destination: List[dict] = []
    
    # Create producer and consumer
    producer = Producer(
        queue=queue,
        source=source,
        name="TaskProducer",
        on_produce=lambda item: print(f"  [Producer] Created task: {item['task']}")
    )
    
    consumer = Consumer(
        queue=queue,
        destination=destination,
        name="TaskConsumer",
        on_consume=lambda item: print(f"  [Consumer] Processed task: {item['task']}")
    )
    
    # Run
    consumer.start()
    producer.start()
    
    producer.join()
    queue.shutdown()
    consumer.join()
    
    print(f"\nProcessed {len(destination)} tasks")
    print(f"Tasks by priority:")
    for priority in range(3):
        count = sum(1 for task in destination if task['priority'] == priority)
        print(f"  Priority {priority}: {count} tasks")


def demo_bounded_buffer():
    """
    Demonstrate the bounded buffer behavior of the blocking queue.
    
    Shows how producers block when queue is full and consumers
    block when queue is empty.
    """
    print("\n" + "=" * 60)
    print("Demo 4: Bounded Buffer Behavior")
    print("=" * 60)
    
    # Small queue to show blocking behavior
    queue = BlockingQueue(capacity=2)
    
    print(f"Queue capacity: {queue.capacity}")
    print("Producer is fast, consumer is slow - observe blocking behavior\n")
    
    source = [f"Data-{i}" for i in range(6)]
    destination: List[str] = []
    
    def on_produce(item):
        print(f"  [Producer] Added {item} | Queue size: {queue.size()}")
    
    def on_consume(item):
        print(f"  [Consumer] Got {item} | Queue size: {queue.size()}")
    
    # Fast producer, slow consumer
    producer = Producer(
        queue=queue,
        source=source,
        name="FastProducer",
        delay=0.05,  # Fast
        on_produce=on_produce
    )
    
    consumer = Consumer(
        queue=queue,
        destination=destination,
        name="SlowConsumer",
        delay=0.2,  # Slow
        on_consume=on_consume
    )
    
    consumer.start()
    producer.start()
    
    producer.join()
    print("\n[Producer finished - waiting for consumer to drain queue]")
    
    queue.shutdown()
    consumer.join()
    
    print(f"\nAll {len(destination)} items transferred successfully")


def demo_context_manager_and_stats():
    """
    Demonstrate context manager usage and queue statistics.
    
    Shows automatic cleanup with 'with' statement and statistics tracking.
    """
    print("\n" + "=" * 60)
    print("Demo 5: Context Manager & Statistics")
    print("=" * 60)
    
    # Using context manager for automatic shutdown
    with BlockingQueue(capacity=3) as queue:
        source = list(range(15))
        destination: List[int] = []
        
        producer = Producer(queue=queue, source=source, delay=0.01)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3, delay=0.02)
        
        consumer.start()
        producer.start()
        
        producer.join()
        # Queue automatically shuts down when exiting 'with' block
    
    consumer.join()
    
    # Note: We need to get stats before shutdown in real usage
    # For demo, showing the concept
    print(f"\nItems transferred: {len(destination)}")
    print("Context manager automatically called shutdown()")
    
    # Demo with statistics
    print("\n--- Statistics Demo ---")
    queue2 = BlockingQueue(capacity=2)
    
    # This will cause blocking since queue is small
    source2 = list(range(10))
    dest2: List[int] = []
    
    producer2 = Producer(queue=queue2, source=source2, delay=0.01)
    consumer2 = Consumer(queue=queue2, destination=dest2, timeout=0.3, delay=0.05)
    
    consumer2.start()
    producer2.start()
    
    producer2.join()
    
    # Get statistics before shutdown
    stats = queue2.get_statistics()
    
    queue2.shutdown()
    consumer2.join()
    
    print(f"Queue Statistics:")
    print(f"  - Total items added: {stats['total_items_added']}")
    print(f"  - Total items removed: {stats['total_items_removed']}")
    print(f"  - Times producer blocked (queue full): {stats['blocked_puts']}")
    print(f"  - Times consumer blocked (queue empty): {stats['blocked_gets']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("  PRODUCER-CONSUMER PATTERN DEMONSTRATION")
    print("  Thread Synchronization with Blocking Queue")
    print("=" * 60)
    
    demo_basic_producer_consumer()
    demo_multiple_producers_consumers()
    demo_with_item_generator()
    demo_bounded_buffer()
    demo_context_manager_and_stats()
    
    print("\n" + "=" * 60)
    print("  All demonstrations completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

