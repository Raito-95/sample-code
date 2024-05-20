from Algorithms.sorting_algorithms_recursion import bubble_sort, merge_sort, quick_sort


def test_bubble_sort():
    assert bubble_sort([34, 21, 10]) == [10, 21, 34]
    assert bubble_sort([]) == []
    assert bubble_sort([1]) == [1]


def test_merge_sort():
    assert merge_sort([34, 21, 10]) == [10, 21, 34]
    assert merge_sort([]) == []
    assert merge_sort([1]) == [1]


def test_quick_sort():
    items = [34, 21, 10]
    assert quick_sort(items, 0, len(items) - 1) == [10, 21, 34]
    assert quick_sort([], 0, 0) == []
    assert quick_sort([1], 0, 0) == [1]
