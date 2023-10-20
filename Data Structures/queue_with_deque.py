from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()  # Use deque to implement the queue

    def enqueue(self, item):
        self.items.append(item)  # Add an element to the end of the queue

    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()  # Remove an element from the front of the queue

    def is_empty(self):
        return len(self.items) == 0  # Check if the queue is empty

    def size(self):
        return len(self.items)  # Get the size of the queue

# Usage example
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
queue.enqueue(3)
