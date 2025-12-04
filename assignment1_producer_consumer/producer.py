"""
Producer Implementation

The Producer class reads items from a source container and places them
into a shared blocking queue for consumption by consumer threads.
"""

import threading
import time
from typing import Any, Callable, Iterable, Optional
from .blocking_queue import BlockingQueue


class Producer(threading.Thread):
    """
    A producer thread that reads from a source and adds items to a shared queue.
    
    The producer reads items from a source container (or generator) and places
    them into a blocking queue. It handles synchronization automatically through
    the BlockingQueue's wait/notify mechanism.
    
    Attributes:
        name (str): Name of the producer thread.
        queue (BlockingQueue): The shared queue to put items into.
        source (Iterable): The source container to read items from.
    """
    
    def __init__(
        self,
        queue: BlockingQueue,
        source: Iterable[Any],
        name: str = "Producer",
        delay: float = 0.0,
        on_produce: Optional[Callable[[Any], None]] = None
    ):
        """
        Initialize the producer.
        
        Args:
            queue: The blocking queue to put items into.
            source: An iterable source of items to produce.
            name: Name for the producer thread.
            delay: Optional delay between producing items (in seconds).
            on_produce: Optional callback called after each item is produced.
        """
        super().__init__(name=name)
        self._queue = queue
        self._source = source
        self._delay = delay
        self._on_produce = on_produce
        self._items_produced = 0
        self._running = False
        self._stop_event = threading.Event()
    
    @property
    def items_produced(self) -> int:
        """Return the number of items produced so far."""
        return self._items_produced
    
    @property
    def is_running(self) -> bool:
        """Return whether the producer is currently running."""
        return self._running
    
    def run(self) -> None:
        """
        Main producer loop.
        
        Reads items from the source and puts them into the queue.
        This method is called when the thread is started.
        """
        self._running = True
        
        try:
            for item in self._source:
                # Check if we should stop
                if self._stop_event.is_set():
                    break
                
                # Try to put item in queue
                success = self._queue.put(item)
                
                if not success:
                    # Queue is shutdown or operation failed
                    break
                
                self._items_produced += 1
                
                # Call callback if provided
                if self._on_produce:
                    self._on_produce(item)
                
                # Optional delay between items
                if self._delay > 0:
                    time.sleep(self._delay)
                    
        finally:
            self._running = False
    
    def stop(self) -> None:
        """
        Signal the producer to stop.
        
        This sets a stop event that will be checked in the main loop.
        The producer will finish processing the current item before stopping.
        """
        self._stop_event.set()
    
    def __repr__(self) -> str:
        return f"Producer(name={self.name}, produced={self._items_produced})"


class ItemGenerator:
    """
    A utility class to generate items for the producer.
    
    This can be used as a source for the Producer when you want to
    generate items programmatically rather than from a fixed list.
    """
    
    def __init__(
        self,
        count: int,
        generator_func: Optional[Callable[[int], Any]] = None
    ):
        """
        Initialize the item generator.
        
        Args:
            count: Number of items to generate.
            generator_func: Optional function that takes an index and returns
                           an item. Defaults to returning the index itself.
        """
        self._count = count
        self._generator_func = generator_func or (lambda i: f"Item-{i}")
    
    def __iter__(self):
        """Iterate over generated items."""
        for i in range(self._count):
            yield self._generator_func(i)
    
    def __len__(self):
        """Return the number of items to generate."""
        return self._count

