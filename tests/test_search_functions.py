import pytest
from Algorithms.search_functions import item_find, binary_search

dataset = [1, 2, 3, 4, 5, 6, 7, 8, 9]

@pytest.mark.parametrize("item,expected", [
    (5, 4),
    (9, 8),
    (1, 0),
    (10, None)
])
def test_item_find(item, expected):
    assert item_find(item, dataset) == expected

@pytest.mark.parametrize("item,expected", [
    (5, 4),
    (9, 8),
    (1, 0),
    (10, None)
])
def test_binary_search(item, expected):
    assert binary_search(item, dataset) == expected
