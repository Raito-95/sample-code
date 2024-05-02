import pytest
from DataStructures.binary_search_tree import BinarySearchTree

@pytest.fixture
def bst():
    bst = BinarySearchTree()
    for value in [5, 3, 7, 2, 4, 6, 8]:
        bst.insert(value)
    return bst

def test_search(bst):
    assert bst.search(4) is True
    assert bst.search(10) is False

def test_insert(bst):
    bst.insert(9)
    assert bst.search(9) is True

def test_delete(bst):
    bst.delete(7)
    assert bst.search(7) is False

def test_inorder_traversal(bst):
    assert bst.inorder_traversal() == [2, 3, 4, 5, 6, 7, 8]

def test_preorder_traversal(bst):
    assert bst.preorder_traversal() == [5, 3, 2, 4, 7, 6, 8]

def test_postorder_traversal(bst):
    assert bst.postorder_traversal() == [2, 4, 3, 6, 8, 7, 5]
