"""
Unit tests for BlockingQueue implementation.

Tests thread synchronization, blocking behavior, and wait/notify mechanism.
"""

import unittest
import threading
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from assignment1_producer_consumer.blocking_queue import BlockingQueue


class TestBlockingQueueBasic(unittest.TestCase):
    """Test basic queue operations."""
    
    def test_init_default_capacity(self):
        """Test queue initialization with default capacity."""
        queue = BlockingQueue()
        self.assertEqual(queue.capacity, 10)
        self.assertTrue(queue.is_empty())
        self.assertFalse(queue.is_full())
    
    def test_init_custom_capacity(self):
        """Test queue initialization with custom capacity."""
        queue = BlockingQueue(capacity=5)
        self.assertEqual(queue.capacity, 5)
    
    def test_init_invalid_capacity(self):
        """Test that invalid capacity raises ValueError."""
        with self.assertRaises(ValueError):
            BlockingQueue(capacity=0)
        with self.assertRaises(ValueError):
            BlockingQueue(capacity=-1)
    
    def test_put_and_get_single_item(self):
        """Test putting and getting a single item."""
        queue = BlockingQueue(capacity=5)
        
        success = queue.put("item1")
        self.assertTrue(success)
        self.assertEqual(queue.size(), 1)
        
        success, item = queue.get()
        self.assertTrue(success)
        self.assertEqual(item, "item1")
        self.assertEqual(queue.size(), 0)
    
    def test_put_and_get_multiple_items(self):
        """Test FIFO order with multiple items."""
        queue = BlockingQueue(capacity=5)
        
        items = ["a", "b", "c", "d"]
        for item in items:
            queue.put(item)
        
        self.assertEqual(queue.size(), 4)
        
        for expected in items:
            success, item = queue.get()
            self.assertTrue(success)
            self.assertEqual(item, expected)
    
    def test_is_empty_and_is_full(self):
        """Test is_empty and is_full properties."""
        queue = BlockingQueue(capacity=2)
        
        self.assertTrue(queue.is_empty())
        self.assertFalse(queue.is_full())
        
        queue.put("item1")
        self.assertFalse(queue.is_empty())
        self.assertFalse(queue.is_full())
        
        queue.put("item2")
        self.assertFalse(queue.is_empty())
        self.assertTrue(queue.is_full())
    
    def test_clear(self):
        """Test clearing the queue."""
        queue = BlockingQueue(capacity=5)
        queue.put("a")
        queue.put("b")
        queue.put("c")
        
        self.assertEqual(queue.size(), 3)
        queue.clear()
        self.assertEqual(queue.size(), 0)
        self.assertTrue(queue.is_empty())


class TestBlockingQueueBlocking(unittest.TestCase):
    """Test blocking behavior and timeouts."""
    
    def test_get_timeout_on_empty_queue(self):
        """Test that get times out on empty queue."""
        queue = BlockingQueue(capacity=5)
        
        start_time = time.time()
        success, item = queue.get(timeout=0.1)
        elapsed = time.time() - start_time
        
        self.assertFalse(success)
        self.assertIsNone(item)
        self.assertGreaterEqual(elapsed, 0.1)
        self.assertLess(elapsed, 0.2)
    
    def test_put_timeout_on_full_queue(self):
        """Test that put times out on full queue."""
        queue = BlockingQueue(capacity=1)
        queue.put("item1")
        
        start_time = time.time()
        success = queue.put("item2", timeout=0.1)
        elapsed = time.time() - start_time
        
        self.assertFalse(success)
        self.assertGreaterEqual(elapsed, 0.1)
        self.assertLess(elapsed, 0.2)
    
    def test_put_blocks_then_succeeds(self):
        """Test that put blocks when full and succeeds after get."""
        queue = BlockingQueue(capacity=1)
        queue.put("item1")
        
        result = {"success": False}
        
        def delayed_get():
            time.sleep(0.1)
            queue.get()
        
        def producer():
            result["success"] = queue.put("item2", timeout=1.0)
        
        getter = threading.Thread(target=delayed_get)
        putter = threading.Thread(target=producer)
        
        putter.start()
        getter.start()
        
        getter.join()
        putter.join()
        
        self.assertTrue(result["success"])
    
    def test_get_blocks_then_succeeds(self):
        """Test that get blocks when empty and succeeds after put."""
        queue = BlockingQueue(capacity=5)
        
        result = {"item": None, "success": False}
        
        def delayed_put():
            time.sleep(0.1)
            queue.put("delayed_item")
        
        def consumer():
            result["success"], result["item"] = queue.get(timeout=1.0)
        
        putter = threading.Thread(target=delayed_put)
        getter = threading.Thread(target=consumer)
        
        getter.start()
        putter.start()
        
        putter.join()
        getter.join()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["item"], "delayed_item")


class TestBlockingQueueShutdown(unittest.TestCase):
    """Test shutdown functionality."""
    
    def test_shutdown_releases_waiting_get(self):
        """Test that shutdown releases threads waiting on get."""
        queue = BlockingQueue(capacity=5)
        
        result = {"completed": False}
        
        def waiting_consumer():
            success, _ = queue.get(timeout=5.0)  # Long timeout
            result["completed"] = True
        
        consumer = threading.Thread(target=waiting_consumer)
        consumer.start()
        
        time.sleep(0.1)  # Let consumer start waiting
        queue.shutdown()
        
        consumer.join(timeout=1.0)
        self.assertTrue(result["completed"])
        self.assertTrue(queue.is_shutdown())
    
    def test_shutdown_releases_waiting_put(self):
        """Test that shutdown releases threads waiting on put."""
        queue = BlockingQueue(capacity=1)
        queue.put("item")  # Fill the queue
        
        result = {"completed": False}
        
        def waiting_producer():
            success = queue.put("item2", timeout=5.0)
            result["completed"] = True
        
        producer = threading.Thread(target=waiting_producer)
        producer.start()
        
        time.sleep(0.1)
        queue.shutdown()
        
        producer.join(timeout=1.0)
        self.assertTrue(result["completed"])
    
    def test_operations_after_shutdown(self):
        """Test that operations return False after shutdown."""
        queue = BlockingQueue(capacity=5)
        queue.put("item")
        queue.shutdown()
        
        self.assertFalse(queue.put("new_item"))
        
        # Should still be able to get existing item
        success, item = queue.get()
        self.assertTrue(success)
        self.assertEqual(item, "item")
        
        # Now queue is empty and shutdown
        success, item = queue.get(timeout=0.1)
        self.assertFalse(success)


class TestBlockingQueueThreadSafety(unittest.TestCase):
    """Test thread safety with concurrent access."""
    
    def test_concurrent_put_and_get(self):
        """Test concurrent producers and consumers."""
        queue = BlockingQueue(capacity=10)
        num_items = 100
        produced = []
        consumed = []
        lock = threading.Lock()
        
        def producer():
            for i in range(num_items // 2):
                item = f"item-{threading.current_thread().name}-{i}"
                queue.put(item)
                with lock:
                    produced.append(item)
        
        def consumer():
            while True:
                success, item = queue.get(timeout=0.5)
                if not success:
                    break
                with lock:
                    consumed.append(item)
        
        producers = [threading.Thread(target=producer, name=f"P{i}") for i in range(2)]
        consumers = [threading.Thread(target=consumer, name=f"C{i}") for i in range(2)]
        
        for c in consumers:
            c.start()
        for p in producers:
            p.start()
        
        for p in producers:
            p.join()
        
        # Wait for queue to drain
        time.sleep(0.6)
        queue.shutdown()
        
        for c in consumers:
            c.join()
        
        self.assertEqual(len(produced), num_items)
        self.assertEqual(len(consumed), num_items)
        self.assertEqual(set(produced), set(consumed))


if __name__ == '__main__':
    unittest.main()

