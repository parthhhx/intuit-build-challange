"""
Unit tests for Producer implementation.

Tests producer functionality, thread behavior, and source handling.
"""

import unittest
import threading
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment1_producer_consumer.blocking_queue import BlockingQueue
from assignment1_producer_consumer.producer import Producer, ItemGenerator


class TestProducerBasic(unittest.TestCase):
    """Test basic producer functionality."""
    
    def test_producer_with_list_source(self):
        """Test producer with a list as source."""
        queue = BlockingQueue(capacity=10)
        source = ["a", "b", "c", "d", "e"]
        
        producer = Producer(queue=queue, source=source, name="TestProducer")
        producer.start()
        producer.join()
        
        self.assertEqual(producer.items_produced, 5)
        self.assertEqual(queue.size(), 5)
    
    def test_producer_with_generator(self):
        """Test producer with a generator function."""
        queue = BlockingQueue(capacity=10)
        
        def gen():
            for i in range(5):
                yield f"gen-{i}"
        
        producer = Producer(queue=queue, source=gen(), name="GenProducer")
        producer.start()
        producer.join()
        
        self.assertEqual(producer.items_produced, 5)
    
    def test_producer_with_item_generator(self):
        """Test producer with ItemGenerator class."""
        queue = BlockingQueue(capacity=10)
        source = ItemGenerator(count=5)
        
        producer = Producer(queue=queue, source=source, name="ItemGenProducer")
        producer.start()
        producer.join()
        
        self.assertEqual(producer.items_produced, 5)
    
    def test_producer_with_custom_generator_func(self):
        """Test ItemGenerator with custom generator function."""
        queue = BlockingQueue(capacity=10)
        
        def custom_gen(i):
            return {"id": i, "value": i * 10}
        
        source = ItemGenerator(count=3, generator_func=custom_gen)
        producer = Producer(queue=queue, source=source)
        producer.start()
        producer.join()
        
        # Verify items
        items = []
        while not queue.is_empty():
            success, item = queue.get()
            items.append(item)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], {"id": 0, "value": 0})
        self.assertEqual(items[1], {"id": 1, "value": 10})
        self.assertEqual(items[2], {"id": 2, "value": 20})
    
    def test_producer_callback(self):
        """Test producer on_produce callback."""
        queue = BlockingQueue(capacity=10)
        source = ["x", "y", "z"]
        produced_items = []
        
        producer = Producer(
            queue=queue,
            source=source,
            on_produce=lambda item: produced_items.append(item)
        )
        producer.start()
        producer.join()
        
        self.assertEqual(produced_items, ["x", "y", "z"])
    
    def test_producer_delay(self):
        """Test producer with delay between items."""
        queue = BlockingQueue(capacity=10)
        source = ["1", "2", "3"]
        
        producer = Producer(queue=queue, source=source, delay=0.05)
        
        start_time = time.time()
        producer.start()
        producer.join()
        elapsed = time.time() - start_time
        
        # Should take at least 0.1s (2 delays between 3 items)
        self.assertGreaterEqual(elapsed, 0.1)
    
    def test_producer_is_running(self):
        """Test is_running property."""
        queue = BlockingQueue(capacity=10)
        source = ["a", "b", "c"]
        
        producer = Producer(queue=queue, source=source, delay=0.1)
        
        self.assertFalse(producer.is_running)
        
        producer.start()
        time.sleep(0.05)
        self.assertTrue(producer.is_running)
        
        producer.join()
        self.assertFalse(producer.is_running)


class TestProducerStop(unittest.TestCase):
    """Test producer stop functionality."""
    
    def test_producer_stop(self):
        """Test stopping producer mid-execution."""
        queue = BlockingQueue(capacity=10)
        source = list(range(100))
        
        producer = Producer(queue=queue, source=source, delay=0.01)
        producer.start()
        
        time.sleep(0.05)
        producer.stop()
        producer.join()
        
        # Should have stopped before processing all items
        self.assertLess(producer.items_produced, 100)
    
    def test_producer_queue_shutdown(self):
        """Test producer behavior when queue is shutdown."""
        queue = BlockingQueue(capacity=2)
        source = list(range(10))
        
        producer = Producer(queue=queue, source=source, delay=0.01)
        producer.start()
        
        time.sleep(0.05)
        queue.shutdown()
        producer.join()
        
        # Producer should have stopped due to queue shutdown
        self.assertLess(producer.items_produced, 10)


class TestProducerBlocking(unittest.TestCase):
    """Test producer blocking behavior when queue is full."""
    
    def test_producer_blocks_on_full_queue(self):
        """Test that producer blocks when queue is full."""
        queue = BlockingQueue(capacity=2)
        source = list(range(5))
        
        producer = Producer(queue=queue, source=source, name="BlockingProducer")
        producer.start()
        
        # Wait a bit - producer should have filled queue and be blocked
        time.sleep(0.1)
        self.assertEqual(queue.size(), 2)
        self.assertTrue(producer.is_running)
        
        # Consume one item to unblock producer
        queue.get()
        time.sleep(0.1)
        
        # Producer should have added another item
        self.assertEqual(queue.size(), 2)
        
        # Drain queue to let producer finish
        while not queue.is_empty():
            queue.get()
        
        producer.join()
        self.assertEqual(producer.items_produced, 5)


class TestItemGenerator(unittest.TestCase):
    """Test ItemGenerator utility class."""
    
    def test_default_generator(self):
        """Test default item generation."""
        gen = ItemGenerator(count=3)
        items = list(gen)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items, ["Item-0", "Item-1", "Item-2"])
    
    def test_custom_generator(self):
        """Test custom generator function."""
        gen = ItemGenerator(count=4, generator_func=lambda i: i ** 2)
        items = list(gen)
        
        self.assertEqual(items, [0, 1, 4, 9])
    
    def test_len(self):
        """Test __len__ method."""
        gen = ItemGenerator(count=10)
        self.assertEqual(len(gen), 10)
    
    def test_iteration_multiple_times(self):
        """Test that generator can be iterated multiple times."""
        gen = ItemGenerator(count=2)
        
        first = list(gen)
        second = list(gen)
        
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()

