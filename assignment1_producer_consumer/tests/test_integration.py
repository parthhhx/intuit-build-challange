"""
Integration tests for the complete Producer-Consumer system.

Tests end-to-end scenarios with producers and consumers working together.
"""

import unittest
import threading
import time
from ..blocking_queue import BlockingQueue
from ..producer import Producer, ItemGenerator
from ..consumer import Consumer, DestinationContainer


class TestProducerConsumerIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def test_single_producer_single_consumer(self):
        """Test basic producer-consumer scenario."""
        queue = BlockingQueue(capacity=5)
        source = [f"item-{i}" for i in range(10)]
        destination = []
        
        producer = Producer(queue=queue, source=source, name="P1")
        consumer = Consumer(queue=queue, destination=destination, name="C1", timeout=0.3)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(producer.items_produced, 10)
        self.assertEqual(consumer.items_consumed, 10)
        self.assertEqual(source, destination)
    
    def test_single_producer_multiple_consumers(self):
        """Test one producer with multiple consumers."""
        queue = BlockingQueue(capacity=5)
        source = list(range(20))
        destination = DestinationContainer()
        
        producer = Producer(queue=queue, source=source, name="Producer")
        consumers = [
            Consumer(queue=queue, destination=destination, name=f"Consumer-{i}", timeout=0.3)
            for i in range(3)
        ]
        
        for c in consumers:
            c.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        
        for c in consumers:
            c.join()
        
        total_consumed = sum(c.items_consumed for c in consumers)
        self.assertEqual(total_consumed, 20)
        self.assertEqual(destination.size(), 20)
        self.assertEqual(sorted(destination.get_all()), source)
    
    def test_multiple_producers_single_consumer(self):
        """Test multiple producers with one consumer."""
        queue = BlockingQueue(capacity=10)
        destination = []
        
        producers = [
            Producer(
                queue=queue,
                source=[f"P{i}-{j}" for j in range(5)],
                name=f"Producer-{i}"
            )
            for i in range(3)
        ]
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        for p in producers:
            p.start()
        
        for p in producers:
            p.join()
        queue.shutdown()
        consumer.join()
        
        total_produced = sum(p.items_produced for p in producers)
        self.assertEqual(total_produced, 15)
        self.assertEqual(consumer.items_consumed, 15)
        self.assertEqual(len(destination), 15)
    
    def test_multiple_producers_multiple_consumers(self):
        """Test multiple producers and consumers."""
        queue = BlockingQueue(capacity=5)
        destination = DestinationContainer()
        
        num_producers = 3
        num_consumers = 4
        items_per_producer = 10
        
        producers = [
            Producer(
                queue=queue,
                source=[f"P{i}-{j}" for j in range(items_per_producer)],
                name=f"Producer-{i}",
                delay=0.001
            )
            for i in range(num_producers)
        ]
        
        consumers = [
            Consumer(
                queue=queue,
                destination=destination,
                name=f"Consumer-{i}",
                timeout=0.3,
                delay=0.001
            )
            for i in range(num_consumers)
        ]
        
        for c in consumers:
            c.start()
        for p in producers:
            p.start()
        
        for p in producers:
            p.join()
        queue.shutdown()
        for c in consumers:
            c.join()
        
        expected_total = num_producers * items_per_producer
        total_produced = sum(p.items_produced for p in producers)
        total_consumed = sum(c.items_consumed for c in consumers)
        
        self.assertEqual(total_produced, expected_total)
        self.assertEqual(total_consumed, expected_total)
        self.assertEqual(destination.size(), expected_total)
    
    def test_fast_producer_slow_consumer(self):
        """Test scenario where producer is faster than consumer."""
        queue = BlockingQueue(capacity=3)
        source = list(range(10))
        destination = []
        
        producer = Producer(queue=queue, source=source, delay=0.01)
        consumer = Consumer(queue=queue, destination=destination, delay=0.05, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        # During execution, queue should often be full
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, source)
    
    def test_slow_producer_fast_consumer(self):
        """Test scenario where consumer is faster than producer."""
        queue = BlockingQueue(capacity=3)
        source = list(range(10))
        destination = []
        
        producer = Producer(queue=queue, source=source, delay=0.05)
        consumer = Consumer(queue=queue, destination=destination, delay=0.01, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        # During execution, queue should often be empty
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, source)
    
    def test_with_item_generator(self):
        """Test with ItemGenerator as source."""
        queue = BlockingQueue(capacity=5)
        
        def generate_data(index):
            return {"id": index, "data": f"payload-{index}"}
        
        source = ItemGenerator(count=15, generator_func=generate_data)
        destination = []
        
        producer = Producer(queue=queue, source=source)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(len(destination), 15)
        self.assertEqual(destination[0], {"id": 0, "data": "payload-0"})
        self.assertEqual(destination[-1], {"id": 14, "data": "payload-14"})
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown during operation."""
        queue = BlockingQueue(capacity=5)
        source = list(range(100))  # Large source
        destination = []
        
        producer = Producer(queue=queue, source=source, delay=0.01)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        # Let some items be processed
        time.sleep(0.2)
        
        # Stop producer
        producer.stop()
        producer.join()
        
        # Shutdown queue
        queue.shutdown()
        consumer.join()
        
        # Verify no items lost that were produced
        self.assertEqual(producer.items_produced, len(destination))
    
    def test_data_integrity(self):
        """Test that all data is transferred correctly without loss or duplication."""
        queue = BlockingQueue(capacity=10)
        destination = DestinationContainer()
        
        # Create unique identifiable items
        num_items = 100
        source = [f"unique-item-{i:04d}" for i in range(num_items)]
        
        producer = Producer(queue=queue, source=source)
        consumers = [
            Consumer(queue=queue, destination=destination, timeout=0.3)
            for _ in range(4)
        ]
        
        for c in consumers:
            c.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        for c in consumers:
            c.join()
        
        result = destination.get_all()
        
        # Check no duplicates
        self.assertEqual(len(result), len(set(result)))
        
        # Check all items present
        self.assertEqual(sorted(result), source)
    
    def test_order_preserved_single_consumer(self):
        """Test FIFO order is preserved with single consumer."""
        queue = BlockingQueue(capacity=5)
        source = list(range(20))
        destination = []
        
        producer = Producer(queue=queue, source=source)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        # Order should be preserved
        self.assertEqual(destination, source)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_empty_source(self):
        """Test producer with empty source."""
        queue = BlockingQueue(capacity=5)
        destination = []
        
        producer = Producer(queue=queue, source=[])
        consumer = Consumer(queue=queue, destination=destination, timeout=0.2)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(producer.items_produced, 0)
        self.assertEqual(consumer.items_consumed, 0)
        self.assertEqual(destination, [])
    
    def test_single_item(self):
        """Test with single item."""
        queue = BlockingQueue(capacity=1)
        destination = []
        
        producer = Producer(queue=queue, source=["only-item"])
        consumer = Consumer(queue=queue, destination=destination, timeout=0.2)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, ["only-item"])
    
    def test_queue_capacity_one(self):
        """Test with minimum queue capacity."""
        queue = BlockingQueue(capacity=1)
        source = list(range(10))
        destination = []
        
        producer = Producer(queue=queue, source=source)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, source)
    
    def test_large_queue_capacity(self):
        """Test with large queue capacity."""
        queue = BlockingQueue(capacity=1000)
        source = list(range(500))
        destination = []
        
        producer = Producer(queue=queue, source=source)
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        consumer.start()
        producer.start()
        
        producer.join()
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, source)


if __name__ == '__main__':
    unittest.main()

