class TreeNode:
    def __init__(self, data):
        self.data = data  # Node data
        self.left = None  # Reference to the left subtree
        self.right = None  # Reference to the right subtree

class BinarySearchTree:
    def __init__(self):
        self.root = None  # Initialize the root node of the binary search tree as None

    def insert(self, data):
        self.root = self._insert_recursive(self.root, data)

    def _insert_recursive(self, node, data):
        if node is None:
            return TreeNode(data)  # Create a new node if the node is None
        if data < node.data:
            node.left = self._insert_recursive(node.left, data)  # Recursively insert into the left subtree
        else:
            node.right = self._insert_recursive(node.right, data)  # Recursively insert into the right subtree
        return node

    def search(self, data):
        return self._search_recursive(self.root, data)

    def _search_recursive(self, node, data):
        if node is None:
            return False  # Not found if the node is None
        if node.data == data:
            return True  # Found if the node's data is equal to the data being searched for
        elif data < node.data:
            return self._search_recursive(node.left, data)  # Recursively search in the left subtree
        else:
            return self._search_recursive(node.right, data)  # Recursively search in the right subtree

# Usage example
bst = BinarySearchTree()
bst.insert(5)
bst.insert(3)
bst.insert(7)
print(bst.search(3))  # True
print(bst.search(6))  # False
