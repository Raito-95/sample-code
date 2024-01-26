import pytest
from Data_Structures.binary_search_tree import BinarySearchTree

def test_bst_insert_and_search():
    bst = BinarySearchTree()
    values_to_insert = [3, 7, 1, 5]

    for value in values_to_insert:
        bst.insert(value)

    for value in values_to_insert:
        assert bst.search(value) is True

    assert bst.search(10) is False
