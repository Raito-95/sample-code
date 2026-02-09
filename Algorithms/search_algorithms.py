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


def binary_search(item, items):
    """
    Performs a binary search to find the index of an item in a sorted list.
    Args:
        item (any): The item to search for.
        items (list): The sorted list in which to search the item.

    Returns:
        int or None: The index of the item if found, None otherwise.
    """
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


def jump_search(item, items):
    """
    Performs a jump search to find the index of an item in a sorted list.
    Args:
        item (any): The item to search for.
        items (list): The sorted list in which to search the item.

    Returns:
        int or None: The index of the item if found, None otherwise.
    """
    n = len(items)
    if n == 0:
        return None
    step = int(n**0.5)
    prev = 0
    while prev < n and items[min(step, n) - 1] < item:
        prev = step
        step += int(n**0.5)
        if prev >= n:
            return None
    while prev < min(step, n):
        if items[prev] == item:
            return prev
        prev += 1
    return None


def exponential_search(item, items):
    """
    Performs an exponential search to find the index of an item in a sorted list.
    Args:
        item (any): The item to search for.
        items (list): The sorted list in which to search the item.

    Returns:
        int or None: The index of the item if found, None otherwise.
    """
    n = len(items)
    if n == 0:
        return None
    if items[0] == item:
        return 0
    index = 1
    while index < n and items[index] < item:
        index *= 2
    return _binary_search_range(item, items, index // 2, min(index, n - 1))


def _binary_search_range(item, items, left, right):
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == item:
            return mid
        if item > items[mid]:
            left = mid + 1
        else:
            right = mid - 1
    return None


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
        print(
            f"Jump Search for {search_item}: Index = {jump_search(search_item, test_items)}"
        )
        print(
            f"Exponential Search for {search_item}: Index = {exponential_search(search_item, test_items)}"
        )


if __name__ == "__main__":
    main()
