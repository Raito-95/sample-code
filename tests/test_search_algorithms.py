from Algorithms.search_algorithms import linear_search, binary_search


def test_linear_search():
    items = [10, 20, 30, 40, 50]
    assert linear_search(30, items) == 2
    assert linear_search(100, items) is None
    assert linear_search(10, items) == 0


def test_binary_search():
    items = [10, 20, 30, 40, 50]
    assert binary_search(30, items) == 2
    assert binary_search(100, items) is None
    assert binary_search(10, items) == 0
