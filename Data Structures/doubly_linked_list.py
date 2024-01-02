class Node:
    def __init__(self, data):
        self.data = data
        self.prev: Node | None = None
        self.next: Node | None = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None  # Initialize the linked list with an empty head node

    def append(self, data):
        new_node = Node(data)  # Create a new node
        if not self.head:
            self.head = new_node  # If the linked list is empty, the new node becomes the head
            return
        current = self.head
        while current.next:
            current = current.next  # Move to the last node in the linked list
        current.next = new_node  # The new node becomes the last node
        new_node.prev = current  # Set the new node's previous node reference to the current last node

# Example of usage
doubly_linked_list = DoublyLinkedList()
doubly_linked_list.append(1)
doubly_linked_list.append(2)
doubly_linked_list.append(3)
