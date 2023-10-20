class TreeNode:
    def __init__(self, data):
        self.data = data  # Node data
        self.left = None  # Reference to the left subtree
        self.right = None  # Reference to the right subtree

class BinaryTree:
    def __init__(self):
        self.root = None  # Initialize the root node of the binary tree as None

# Usage example
binary_tree = BinaryTree()
binary_tree.root = TreeNode(1)  # Create the root node with data 1
binary_tree.root.left = TreeNode(2)  # Create a node in the left subtree with data 2
binary_tree.root.right = TreeNode(3)  # Create a node in the right subtree with data 3
