from core.algorithms.list_analysis_functions import is_sorted, find_max


def test_is_sorted():
    assert is_sorted([1, 2, 3, 4, 5])
    assert not is_sorted([5, 4, 3, 2, 1])
    assert is_sorted([])  # Empty list is considered sorted
    assert is_sorted([1])  # Single element list is sorted


def test_find_max():
    assert find_max([1, 2, 3, 4, 5]) == 5
    assert find_max([5, 4, 3, 2, 1]) == 5
    assert find_max([]) is None
    assert find_max([1]) == 1

