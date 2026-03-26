class Stack:
    def __init__(self):
        self.items = []  # Use a list to implement the stack

    def push(self, item):
        """
        Push an item onto the top of the stack.
        """
        self.items.append(item)

    def pop(self):
        """
        Pop the item from the top of the stack.
        Returns the popped item if the stack is not empty, otherwise None.
        """
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """
        Return the item at the top of the stack without removing it.
        Returns None if the stack is empty.
        """
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        """
        Check if the stack is empty.
        Returns True if the stack is empty, otherwise False.
        """
        return len(self.items) == 0

    def size(self):
        """
        Return the size of the stack (number of elements).
        """
        return len(self.items)

    def display(self):
        """
        Display all items in the stack.
        """
        return list(reversed(self.items))  # Display from top to bottom


def main():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    print("Current Stack:", stack.display())
    print("Top item:", stack.peek())
    print("Popped item:", stack.pop())
    print("Stack after pop:", stack.display())


if __name__ == "__main__":
    main()
