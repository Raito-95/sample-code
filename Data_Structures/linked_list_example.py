# Define the Node class
class Node:
    def __init__(self, data):
        self.data = data  # Store data
        self.next: Node | None = None

# Define the LinkedList class
class LinkedList:
    def __init__(self):
        self.head = None  # Head node of the linked list

    # Append a node to the end of the linked list
    def append(self, data):
        new_node = Node(data)  # Create a new node
        if not self.head:  # If the list is empty
            self.head = new_node  # Set the new node as the head
            return
        current = self.head  # Start from the head
        while current.next:
            current = current.next
        current.next = new_node  # Connect the new node to the end

# Usage example
linked_list = LinkedList()  # Create a linked list object
linked_list.append(1)  # Append node 1
linked_list.append(2)  # Append node 2
linked_list.append(3)  # Append node 3
