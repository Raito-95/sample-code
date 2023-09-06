class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

# 使用示例
binary_tree = BinaryTree()
binary_tree.root = TreeNode(1)
binary_tree.root.left = TreeNode(2)
binary_tree.root.right = TreeNode(3)
