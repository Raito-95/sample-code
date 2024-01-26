# Define the Stack class
class Stack:
    def __init__(self):
        self.items = []  # Use a list to implement the stack

    # Push an item onto the top of the stack
    def push(self, item):
        self.items.append(item)

    # Pop the item from the top of the stack
    def pop(self):
        if not self.is_empty():  # Check if the stack is empty
            return self.items.pop()

    # Check if the stack is empty
    def is_empty(self):
        return len(self.items) == 0

    # Return the item at the top of the stack without removing it
    def peek(self):
        if not self.is_empty():  # Check if the stack is empty
            return self.items[-1]

    # Return the size of the stack (number of elements)
    def size(self):
        return len(self.items)

# Example of usage
stack = Stack()  # Create a stack object
stack.push(1)  # Push item 1 onto the stack
stack.push(2)  # Push item 2 onto the stack
stack.push(3)  # Push item 3 onto the stack
