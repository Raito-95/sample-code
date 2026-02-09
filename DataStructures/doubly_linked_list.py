class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        """
        Append a node with the given data to the end of the list.
        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node
        new_node.prev = last

    def delete(self, node):
        """
        Delete the specified node from the list.
        """
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if node == self.head:
            self.head = node.next
        node.prev = node.next = None

    def find(self, data):
        """
        Find and return the first node with the specified data.
        Returns None if no such node exists.
        """
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next
        return None

    def display_forward(self):
        """
        Display the elements of the list from the head to the tail.
        """
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements

    def display_backward(self):
        """
        Display the elements of the list from the tail to the head.
        """
        elements = []
        current = self.head
        if not current:
            return elements
        while current.next:
            current = current.next
        while current:
            elements.append(current.data)
            current = current.prev
        return elements


if __name__ == "__main__":
    # Usage example
    dll = DoublyLinkedList()
    dll.append(1)
    dll.append(2)
    dll.append(3)
    print("Forward:", dll.display_forward())  # Output: [1, 2, 3]
    print("Backward:", dll.display_backward())  # Output: [3, 2, 1]

    node = dll.find(2)
    if node:
        dll.delete(node)
    print("Forward after deletion:", dll.display_forward())  # Output: [1, 3]
