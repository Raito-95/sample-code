from Algorithms.sorting_and_recursion import is_sorted, find_max

def test_is_sorted():
    assert is_sorted([1, 2, 3, 4, 5]) == True
    assert is_sorted([5, 4, 3, 2, 1]) == False

def test_find_max():
    assert find_max([1, 2, 3, 4, 5]) == 5
    assert find_max([5, 4, 3, 2, 1]) == 5
