def linear_search(item, items):
    """
    Performs a linear search to find the index of an item in a list.
    Args:
        item (any): The item to search for.
        items (list): The list in which to search the item.

    Returns:
        int or None: The index of the item if found, None otherwise.
    """
    for index, current_item in enumerate(items):
        if current_item == item:
            return index
    return None  # Item not found


def _is_non_decreasing(items):
    """Return True when items are sorted in non-decreasing order."""
    return all(items[index] <= items[index + 1] for index in range(len(items) - 1))


def binary_search(item, items):
    """
    Performs a binary search to find the index of an item in a sorted list.
    Args:
        item (any): The item to search for.
        items (list): The sorted list in which to search the item.

    Returns:
        int or None: The index of the item if found, None otherwise.

    Raises:
        ValueError: If ``items`` is not sorted in non-decreasing order.
    """
    if not _is_non_decreasing(items):
        raise ValueError("binary_search requires a sorted list in non-decreasing order")

    first, last = 0, len(items) - 1
    while first <= last:
        mid = (first + last) // 2
        if items[mid] == item:
            return mid
        elif item > items[mid]:
            first = mid + 1
        else:
            last = mid - 1
    return None  # Item not found


def main():
    """
    Main function to demonstrate the functionality of search algorithms with various test cases.
    """
    test_items = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    test_searches = [30, 70, 110]

    for search_item in test_searches:
        print(
            f"Linear Search for {search_item}: Index = {linear_search(search_item, test_items)}"
        )
        print(
            f"Binary Search for {search_item}: Index = {binary_search(search_item, test_items)}"
        )


if __name__ == "__main__":
    main()
