"""
Consumer Implementation

The Consumer class reads items from a shared blocking queue and stores
them in a destination container.
"""

import threading
import time
from typing import Any, Callable, List, Optional
from .blocking_queue import BlockingQueue


class Consumer(threading.Thread):
    """
    A consumer thread that reads from a shared queue and stores items.
    
    The consumer takes items from a blocking queue and stores them in a
    destination container. It handles synchronization automatically through
    the BlockingQueue's wait/notify mechanism.
    
    Attributes:
        name (str): Name of the consumer thread.
        queue (BlockingQueue): The shared queue to get items from.
        destination (List): The destination container to store items.
    """
    
    def __init__(
        self,
        queue: BlockingQueue,
        destination: Optional[List[Any]] = None,
        name: str = "Consumer",
        delay: float = 0.0,
        on_consume: Optional[Callable[[Any], None]] = None,
        timeout: Optional[float] = 1.0
    ):
        """
        Initialize the consumer.
        
        Args:
            queue: The blocking queue to get items from.
            destination: Optional list to store consumed items. If None,
                        a new list will be created.
            name: Name for the consumer thread.
            delay: Optional delay between consuming items (in seconds).
            on_consume: Optional callback called after each item is consumed.
            timeout: Timeout for queue.get() operations. Allows checking
                    for stop signals periodically.
        """
        super().__init__(name=name)
        self._queue = queue
        self._destination = destination if destination is not None else []
        self._delay = delay
        self._on_consume = on_consume
        self._timeout = timeout
        self._items_consumed = 0
        self._running = False
        self._stop_event = threading.Event()
    
    @property
    def items_consumed(self) -> int:
        """Return the number of items consumed so far."""
        return self._items_consumed
    
    @property
    def is_running(self) -> bool:
        """Return whether the consumer is currently running."""
        return self._running
    
    @property
    def destination(self) -> List[Any]:
        """Return the destination container with consumed items."""
        return self._destination
    
    def run(self) -> None:
        """
        Main consumer loop.
        
        Gets items from the queue and stores them in the destination.
        This method is called when the thread is started.
        """
        self._running = True
        
        try:
            while not self._stop_event.is_set():
                # Try to get item from queue with timeout
                success, item = self._queue.get(timeout=self._timeout)
                
                if not success:
                    # Check if queue is shutdown and empty
                    if self._queue.is_shutdown() and self._queue.is_empty():
                        break
                    # Otherwise, it was just a timeout - continue loop
                    continue
                
                # Store item in destination
                self._destination.append(item)
                self._items_consumed += 1
                
                # Call callback if provided
                if self._on_consume:
                    self._on_consume(item)
                
                # Optional delay between items
                if self._delay > 0:
                    time.sleep(self._delay)
                    
        finally:
            self._running = False
    
    def stop(self) -> None:
        """
        Signal the consumer to stop.
        
        This sets a stop event that will be checked in the main loop.
        The consumer will finish processing the current item before stopping.
        """
        self._stop_event.set()
    
    def get_results(self) -> List[Any]:
        """
        Get a copy of the consumed items.
        
        Returns:
            A list containing all items consumed so far.
        """
        return list(self._destination)
    
    def __repr__(self) -> str:
        return f"Consumer(name={self.name}, consumed={self._items_consumed})"


class DestinationContainer:
    """
    A thread-safe destination container for storing consumed items.
    
    Use this when multiple consumers need to write to the same destination.
    """
    
    def __init__(self):
        """Initialize the thread-safe container."""
        self._items: List[Any] = []
        self._lock = threading.Lock()
    
    def append(self, item: Any) -> None:
        """
        Add an item to the container (thread-safe).
        
        Args:
            item: The item to add.
        """
        with self._lock:
            self._items.append(item)
    
    def get_all(self) -> List[Any]:
        """
        Get a copy of all items in the container.
        
        Returns:
            A list containing all stored items.
        """
        with self._lock:
            return list(self._items)
    
    def size(self) -> int:
        """
        Return the number of items in the container.
        
        Returns:
            The count of items stored.
        """
        with self._lock:
            return len(self._items)
    
    def clear(self) -> None:
        """Remove all items from the container."""
        with self._lock:
            self._items.clear()
    
    def __len__(self) -> int:
        return self.size()

