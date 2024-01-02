class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None

class BinaryTree:
    def __init__(self):
        self.root: TreeNode | None = None

# Usage example
binary_tree = BinaryTree()
binary_tree.root = TreeNode(1)
binary_tree.root.left = TreeNode(2)
binary_tree.root.right = TreeNode(3)