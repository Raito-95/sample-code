class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, data):
        self.root = self._insert_recursive(self.root, data)

    def _insert_recursive(self, node, data):
        if node is None:
            return TreeNode(data)
        if data < node.data:
            node.left = self._insert_recursive(node.left, data)
        else:
            node.right = self._insert_recursive(node.right, data)
        return node

    def search(self, data):
        return self._search_recursive(self.root, data)

    def _search_recursive(self, node, data):
        if node is None:
            return False
        if node.data == data:
            return True
        elif data < node.data:
            return self._search_recursive(node.left, data)
        else:
            return self._search_recursive(node.right, data)

    def delete(self, data):
        self.root = self._delete_recursive(self.root, data)

    def _delete_recursive(self, node, data):
        if node is None:
            return node
        if data < node.data:
            node.left = self._delete_recursive(node.left, data)
        elif data > node.data:
            node.right = self._delete_recursive(node.right, data)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            temp_val = self._min_value_node(node.right)
            node.data = temp_val.data
            node.right = self._delete_recursive(node.right, temp_val.data)
        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def inorder_traversal(self):
        return self._inorder_recursive(self.root)

    def _inorder_recursive(self, node):
        res = []
        if node:
            res = self._inorder_recursive(node.left)
            res.append(node.data)
            res = res + self._inorder_recursive(node.right)
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
            res = self._postorder_recursive(node.left)
            res = res + self._postorder_recursive(node.right)
            res.append(node.data)
        return res

# Usage example
bst = BinarySearchTree()
bst.insert(5)
bst.insert(3)
bst.insert(7)
bst.insert(2)
bst.insert(4)
bst.insert(6)
bst.insert(8)

print("Inorder traversal:", bst.inorder_traversal())
print("Preorder traversal:", bst.preorder_traversal())
print("Postorder traversal:", bst.postorder_traversal())
print("Search for 4:", bst.search(4))
bst.delete(7)
print("Inorder traversal after deleting 7:", bst.inorder_traversal())
