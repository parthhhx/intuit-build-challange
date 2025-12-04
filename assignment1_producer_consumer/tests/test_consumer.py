"""
Unit tests for Consumer implementation.

Tests consumer functionality, thread behavior, and destination handling.
"""

import unittest
import threading
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment1_producer_consumer.blocking_queue import BlockingQueue
from assignment1_producer_consumer.consumer import Consumer, DestinationContainer


class TestConsumerBasic(unittest.TestCase):
    """Test basic consumer functionality."""
    
    def test_consumer_consumes_items(self):
        """Test consumer retrieves items from queue."""
        queue = BlockingQueue(capacity=10)
        destination = []
        
        # Pre-fill queue
        for item in ["a", "b", "c"]:
            queue.put(item)
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.1)
        consumer.start()
        
        time.sleep(0.3)  # Allow consumer to process
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(consumer.items_consumed, 3)
        self.assertEqual(destination, ["a", "b", "c"])
    
    def test_consumer_creates_own_destination(self):
        """Test consumer creates destination if not provided."""
        queue = BlockingQueue(capacity=10)
        queue.put("item1")
        
        consumer = Consumer(queue=queue, timeout=0.1)
        consumer.start()
        
        time.sleep(0.2)
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(consumer.destination, ["item1"])
    
    def test_consumer_callback(self):
        """Test consumer on_consume callback."""
        queue = BlockingQueue(capacity=10)
        consumed_items = []
        
        for item in ["x", "y", "z"]:
            queue.put(item)
        
        consumer = Consumer(
            queue=queue,
            on_consume=lambda item: consumed_items.append(f"processed-{item}"),
            timeout=0.1
        )
        consumer.start()
        
        time.sleep(0.3)
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(consumed_items, ["processed-x", "processed-y", "processed-z"])
    
    def test_consumer_delay(self):
        """Test consumer with delay between items."""
        queue = BlockingQueue(capacity=10)
        
        for item in ["1", "2", "3"]:
            queue.put(item)
        
        consumer = Consumer(queue=queue, delay=0.05, timeout=0.1)
        
        start_time = time.time()
        consumer.start()
        
        time.sleep(0.3)
        queue.shutdown()
        consumer.join()
        elapsed = time.time() - start_time
        
        # Should have taken at least 0.1s for delays
        self.assertGreaterEqual(elapsed, 0.1)
    
    def test_consumer_get_results(self):
        """Test get_results returns copy of destination."""
        queue = BlockingQueue(capacity=10)
        destination = ["initial"]
        
        queue.put("added")
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.1)
        consumer.start()
        
        time.sleep(0.2)
        queue.shutdown()
        consumer.join()
        
        results = consumer.get_results()
        self.assertEqual(results, ["initial", "added"])
        
        # Verify it's a copy
        results.append("modified")
        self.assertEqual(consumer.destination, ["initial", "added"])


class TestConsumerBlocking(unittest.TestCase):
    """Test consumer blocking behavior."""
    
    def test_consumer_waits_for_items(self):
        """Test that consumer waits when queue is empty."""
        queue = BlockingQueue(capacity=10)
        destination = []
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.5)
        consumer.start()
        
        # Consumer should be waiting
        time.sleep(0.1)
        self.assertTrue(consumer.is_running)
        self.assertEqual(len(destination), 0)
        
        # Add item - consumer should pick it up
        queue.put("delayed_item")
        time.sleep(0.2)
        
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, ["delayed_item"])
    
    def test_consumer_continues_after_item_added(self):
        """Test consumer continues when items are added."""
        queue = BlockingQueue(capacity=10)
        destination = []
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        consumer.start()
        
        # Add items with delays
        time.sleep(0.1)
        queue.put("item1")
        time.sleep(0.1)
        queue.put("item2")
        
        time.sleep(0.2)
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, ["item1", "item2"])


class TestConsumerStop(unittest.TestCase):
    """Test consumer stop functionality."""
    
    def test_consumer_stop(self):
        """Test stopping consumer."""
        queue = BlockingQueue(capacity=10)
        
        # Add many items
        for i in range(20):
            queue.put(f"item-{i}")
        
        consumer = Consumer(queue=queue, delay=0.02, timeout=0.5)
        consumer.start()
        
        time.sleep(0.1)
        consumer.stop()
        consumer.join()
        
        # Should have stopped before processing all items
        self.assertLess(consumer.items_consumed, 20)
    
    def test_consumer_stops_on_queue_shutdown(self):
        """Test consumer stops when queue is shutdown and empty."""
        queue = BlockingQueue(capacity=10)
        queue.put("item")
        
        consumer = Consumer(queue=queue, timeout=0.1)
        consumer.start()
        
        time.sleep(0.2)
        queue.shutdown()
        consumer.join(timeout=1.0)
        
        self.assertFalse(consumer.is_running)


class TestDestinationContainer(unittest.TestCase):
    """Test DestinationContainer thread-safe container."""
    
    def test_basic_operations(self):
        """Test basic container operations."""
        container = DestinationContainer()
        
        self.assertEqual(container.size(), 0)
        self.assertEqual(len(container), 0)
        
        container.append("item1")
        container.append("item2")
        
        self.assertEqual(container.size(), 2)
        self.assertEqual(container.get_all(), ["item1", "item2"])
    
    def test_clear(self):
        """Test clearing the container."""
        container = DestinationContainer()
        container.append("a")
        container.append("b")
        
        container.clear()
        
        self.assertEqual(container.size(), 0)
        self.assertEqual(container.get_all(), [])
    
    def test_get_all_returns_copy(self):
        """Test that get_all returns a copy."""
        container = DestinationContainer()
        container.append("original")
        
        items = container.get_all()
        items.append("modified")
        
        self.assertEqual(container.get_all(), ["original"])
    
    def test_thread_safety(self):
        """Test thread-safe concurrent access."""
        container = DestinationContainer()
        num_threads = 5
        items_per_thread = 100
        
        def append_items(thread_id):
            for i in range(items_per_thread):
                container.append(f"t{thread_id}-{i}")
        
        threads = [
            threading.Thread(target=append_items, args=(i,))
            for i in range(num_threads)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(container.size(), num_threads * items_per_thread)


class TestConsumerIntegration(unittest.TestCase):
    """Integration tests with producer-like behavior."""
    
    def test_consumer_with_producer_thread(self):
        """Test consumer working with a simulated producer."""
        queue = BlockingQueue(capacity=5)
        destination = []
        items_to_produce = ["a", "b", "c", "d", "e"]
        
        def producer():
            for item in items_to_produce:
                queue.put(item)
                time.sleep(0.02)
        
        consumer = Consumer(queue=queue, destination=destination, timeout=0.3)
        
        producer_thread = threading.Thread(target=producer)
        consumer.start()
        producer_thread.start()
        
        producer_thread.join()
        time.sleep(0.2)
        queue.shutdown()
        consumer.join()
        
        self.assertEqual(destination, items_to_produce)
    
    def test_multiple_consumers_with_destination_container(self):
        """Test multiple consumers sharing a DestinationContainer."""
        queue = BlockingQueue(capacity=10)
        destination = DestinationContainer()
        
        # Fill queue
        for i in range(20):
            queue.put(f"item-{i}")
        
        consumers = [
            Consumer(queue=queue, destination=destination, timeout=0.1, name=f"C{i}")
            for i in range(3)
        ]
        
        for c in consumers:
            c.start()
        
        time.sleep(0.5)
        queue.shutdown()
        
        for c in consumers:
            c.join()
        
        total_consumed = sum(c.items_consumed for c in consumers)
        self.assertEqual(total_consumed, 20)
        self.assertEqual(destination.size(), 20)


if __name__ == '__main__':
    unittest.main()

