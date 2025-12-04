"""
Blocking Queue Implementation

A thread-safe blocking queue that implements the wait/notify mechanism
using Python's threading.Condition for synchronization between
producer and consumer threads.
"""

import threading
import logging
from typing import Any, Optional, Tuple
from collections import deque

# Configure module logger
logger = logging.getLogger(__name__)


class BlockingQueue:
    """
    A thread-safe blocking queue with bounded capacity.
    
    This queue blocks producers when full and consumers when empty,
    using threading.Condition for wait/notify synchronization.
    
    Attributes:
        capacity (int): Maximum number of items the queue can hold.
    """
    
    def __init__(self, capacity: int = 10):
        """
        Initialize the blocking queue.
        
        Args:
            capacity: Maximum capacity of the queue. Default is 10.
        
        Raises:
            ValueError: If capacity is less than 1.
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        
        self._capacity = capacity
        self._queue: deque = deque()
        self._lock = threading.Lock()
        
        # Condition variable for wait/notify mechanism
        # not_full: signaled when queue has space available
        # not_empty: signaled when queue has items available
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)
        
        # Flag to signal shutdown
        self._shutdown = False
        
        # Statistics tracking
        self._total_items_added = 0
        self._total_items_removed = 0
        self._total_blocked_puts = 0
        self._total_blocked_gets = 0
    
    @property
    def capacity(self) -> int:
        """Return the maximum capacity of the queue."""
        return self._capacity
    
    def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """
        Add an item to the queue, blocking if full.
        
        This method blocks the calling thread if the queue is at capacity,
        waiting until space becomes available or timeout expires.
        
        Args:
            item: The item to add to the queue.
            timeout: Maximum time to wait in seconds. None means wait forever.
        
        Returns:
            True if item was added successfully, False if timeout expired
            or queue is shutdown.
        """
        with self._not_full:
            # Wait while queue is full (and not shutdown)
            blocked = False
            while len(self._queue) >= self._capacity and not self._shutdown:
                if not blocked:
                    self._total_blocked_puts += 1
                    blocked = True
                if not self._not_full.wait(timeout=timeout):
                    # Timeout expired
                    return False
            
            if self._shutdown:
                return False
            
            # Add item to queue
            self._queue.append(item)
            self._total_items_added += 1
            
            # Notify waiting consumers that queue is not empty
            self._not_empty.notify()
            
            return True
    
    def get(self, timeout: Optional[float] = None) -> Tuple[bool, Any]:
        """
        Remove and return an item from the queue, blocking if empty.
        
        This method blocks the calling thread if the queue is empty,
        waiting until an item becomes available or timeout expires.
        
        Args:
            timeout: Maximum time to wait in seconds. None means wait forever.
        
        Returns:
            A tuple (success, item) where success is True if an item was
            retrieved, False if timeout expired or queue is shutdown.
            When success is False, item is None.
        """
        with self._not_empty:
            # Wait while queue is empty (and not shutdown)
            blocked = False
            while len(self._queue) == 0 and not self._shutdown:
                if not blocked:
                    self._total_blocked_gets += 1
                    blocked = True
                if not self._not_empty.wait(timeout=timeout):
                    # Timeout expired
                    return (False, None)
            
            if self._shutdown and len(self._queue) == 0:
                return (False, None)
            
            # Remove item from queue
            item = self._queue.popleft()
            self._total_items_removed += 1
            
            # Notify waiting producers that queue is not full
            self._not_full.notify()
            
            return (True, item)
    
    def size(self) -> int:
        """
        Return the current number of items in the queue.
        
        Returns:
            The number of items currently in the queue.
        """
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue has no items, False otherwise.
        """
        with self._lock:
            return len(self._queue) == 0
    
    def is_full(self) -> bool:
        """
        Check if the queue is at capacity.
        
        Returns:
            True if the queue is full, False otherwise.
        """
        with self._lock:
            return len(self._queue) >= self._capacity
    
    def shutdown(self) -> None:
        """
        Shutdown the queue, releasing all waiting threads.
        
        After shutdown, put() and get() operations will return False
        immediately without blocking.
        """
        with self._lock:
            self._shutdown = True
            # Wake up all waiting threads
            self._not_full.notify_all()
            self._not_empty.notify_all()
    
    def is_shutdown(self) -> bool:
        """
        Check if the queue has been shutdown.
        
        Returns:
            True if shutdown() has been called, False otherwise.
        """
        with self._lock:
            return self._shutdown
    
    def clear(self) -> None:
        """
        Remove all items from the queue.
        
        This operation is thread-safe and will notify any waiting producers.
        """
        with self._lock:
            self._queue.clear()
            self._not_full.notify_all()
    
    def __enter__(self) -> 'BlockingQueue':
        """Context manager entry - returns the queue instance."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - automatically shuts down the queue."""
        self.shutdown()
    
    def __len__(self) -> int:
        """Return the current size of the queue."""
        return self.size()
    
    def __repr__(self) -> str:
        """Return string representation of the queue."""
        return f"BlockingQueue(capacity={self._capacity}, size={self.size()}, shutdown={self._shutdown})"
    
    def get_statistics(self) -> dict:
        """
        Get queue statistics.
        
        Returns:
            Dictionary containing queue statistics:
            - total_items_added: Total items ever added
            - total_items_removed: Total items ever removed
            - blocked_puts: Times put() had to wait
            - blocked_gets: Times get() had to wait
        """
        with self._lock:
            return {
                "total_items_added": self._total_items_added,
                "total_items_removed": self._total_items_removed,
                "blocked_puts": self._total_blocked_puts,
                "blocked_gets": self._total_blocked_gets,
                "current_size": len(self._queue),
                "capacity": self._capacity
            }

