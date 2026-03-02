def is_sorted(items):
    """
    Checks if the given list of items is sorted in non-decreasing order.
    Args:
        items (list): The list to be checked.

    Returns:
        bool: True if the list is sorted, False otherwise.
    """
    if not items:  # Handle the case for an empty list
        return True  # An empty list is considered sorted
    return all(items[i] <= items[i + 1] for i in range(len(items) - 1))


def find_max(items):
    """
    Finds the maximum value in a list using a recursive approach.
    Args:
        items (list): The list from which to find the maximum value.

    Returns:
        int or None: The maximum value found in the list, or None if the list is empty.
    """
    if not items:
        return None  # Return None if the list is empty
    if len(items) == 1:
        return items[0]  # Return the only element if the list contains one item

    # Recursive case: Calculate the maximum of the first element and the max of the rest
    op1 = items[0]
    op2 = find_max(items[1:])
    return op1 if op1 > op2 else op2


def main():
    """
    Main function to demonstrate the functionality of list analysis functions.
    """
    test_lists = [
        [],
        [1],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
    ]
    for lst in test_lists:
        print(f"List: {lst} Is sorted: {is_sorted(lst)} Max value: {find_max(lst)}")


if __name__ == "__main__":
    main()
