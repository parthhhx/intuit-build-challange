"""
Assignment 1: Producer-Consumer Pattern with Thread Synchronization

This module implements a classic producer-consumer pattern demonstrating:
- Thread synchronization
- Concurrent programming
- Blocking queues
- Wait/Notify mechanism using threading.Condition
"""

from .blocking_queue import BlockingQueue
from .producer import Producer
from .consumer import Consumer

__all__ = ['BlockingQueue', 'Producer', 'Consumer']

