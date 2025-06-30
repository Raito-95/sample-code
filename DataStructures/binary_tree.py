class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert_left(self, parent, data):
        new_node = TreeNode(data)
        if parent.left is None:
            parent.left = new_node
        else:
            new_node.left = parent.left
            parent.left = new_node

    def insert_right(self, parent, data):
        new_node = TreeNode(data)
        if parent.right is None:
            parent.right = new_node
        else:
            new_node.right = parent.right
            parent.right = new_node

    def inorder_traversal(self):
        return self._inorder_recursive(self.root)

    def _inorder_recursive(self, node):
        res = []
        if node:
            res.extend(self._inorder_recursive(node.left))
            res.append(node.data)
            res.extend(self._inorder_recursive(node.right))
        return res

    def preorder_traversal(self):
        return self._preorder_recursive(self.root)

    def _preorder_recursive(self, node):
        res = []
        if node:
            res.append(node.data)
            res.extend(self._preorder_recursive(node.left))
            res.extend(self._preorder_recursive(node.right))
        return res

    def postorder_traversal(self):
        return self._postorder_recursive(self.root)

    def _postorder_recursive(self, node):
        res = []
        if node:
            res.extend(self._postorder_recursive(node.left))
            res.extend(self._postorder_recursive(node.right))
            res.append(node.data)
        return res


if __name__ == "__main__":
    # Usage example
    binary_tree = BinaryTree()
    root = TreeNode(1)
    binary_tree.root = root
    binary_tree.insert_left(root, 2)
    binary_tree.insert_right(root, 3)
    binary_tree.insert_left(root.left, 4)
    binary_tree.insert_right(root.right, 5)

    print("Inorder traversal:", binary_tree.inorder_traversal())
    print("Preorder traversal:", binary_tree.preorder_traversal())
    print("Postorder traversal:", binary_tree.postorder_traversal())
