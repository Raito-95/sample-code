from collections import deque


class Queue:
    def __init__(self):
        self.items = deque()  # Use deque to implement the queue

    def enqueue(self, item):
        """
        Add an element to the end of the queue.
        """
        self.items.append(item)

    def dequeue(self):
        """
        Remove an element from the front of the queue.
        Returns the element if the queue is not empty, otherwise None.
        """
        if not self.is_empty():
            return self.items.popleft()
        return None

    def is_empty(self):
        """
        Check if the queue is empty.
        Returns True if empty, False otherwise.
        """
        return len(self.items) == 0

    def size(self):
        """
        Get the size of the queue.
        Returns the number of elements in the queue.
        """
        return len(self.items)

    def peek(self):
        """
        Get the front item from the queue without removing it.
        Returns the front item if the queue is not empty, otherwise None.
        """
        if not self.is_empty():
            return self.items[0]
        return None


# Usage example
if __name__ == "__main__":
    queue = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    print("Front item:", queue.peek())  # Output should be 1
    print("Queue size:", queue.size())  # Output should be 3
    dequeued_item = queue.dequeue()  # Should dequeue 1
    print("Dequeued item:", dequeued_item)
    print("New front item:", queue.peek())  # Output should be 2
    print("New queue size:", queue.size())  # Output should be 2
