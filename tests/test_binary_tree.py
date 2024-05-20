import pytest
from DataStructures.binary_tree import BinaryTree, TreeNode


@pytest.fixture
def binary_tree():
    bt = BinaryTree()
    bt.root = TreeNode(1)
    bt.insert_left(bt.root, 2)
    bt.insert_right(bt.root, 3)
    bt.insert_left(bt.root.left, 4)
    bt.insert_right(bt.root.right, 5)
    return bt


def test_inorder_traversal(binary_tree):
    assert binary_tree.inorder_traversal() == [4, 2, 1, 3, 5]


def test_preorder_traversal(binary_tree):
    assert binary_tree.preorder_traversal() == [1, 2, 4, 3, 5]


def test_postorder_traversal(binary_tree):
    assert binary_tree.postorder_traversal() == [4, 2, 5, 3, 1]
