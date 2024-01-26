from Algorithms.sorting_algorithms import bubble_sort, merge_sort, quick_sort

def test_bubble_sort():
    assert bubble_sort([3, 2, 1, 4, 5]) == [1, 2, 3, 4, 5]

def test_merge_sort():
    assert merge_sort([3, 2, 1, 4, 5]) == [1, 2, 3, 4, 5]

def test_quick_sort():
    data = [3, 2, 1, 4, 5]
    assert quick_sort(0, len(data) - 1, data) == [1, 2, 3, 4, 5]
