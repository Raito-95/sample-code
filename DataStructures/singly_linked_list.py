class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        """
        Append a new node with the given data to the end of the list.
        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def delete_node(self, key):
        """
        Delete the first occurrence of the node that contains the data key.
        """
        current = self.head
        previous = None
        while current and current.data != key:
            previous = current
            current = current.next

        if current is None:
            return  # The data not found in the list

        if previous is None:
            self.head = current.next  # The node to delete is the head
        else:
            previous.next = current.next  # Bypass the node to delete

    def search(self, key):
        """
        Search for a node with the specified data.
        Returns True if found, False otherwise.
        """
        current = self.head
        while current:
            if current.data == key:
                return True
            current = current.next
        return False

    def reverse(self):
        """
        Reverse the singly linked list.
        """
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    def display(self):
        """
        Display all the elements of the list.
        """
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements


# Usage example
if __name__ == "__main__":
    sll = SinglyLinkedList()
    sll.append(1)
    sll.append(2)
    sll.append(3)
    print("Original List:", sll.display())  # Output should be [1, 2, 3]
    sll.delete_node(2)
    print("After Deleting 2:", sll.display())  # Output should be [1, 3]
    print("Search for 3:", sll.search(3))  # Output should be True
    sll.reverse()
    print("Reversed List:", sll.display())  # Output should be [3, 1]
