# Given sorted dataset
dataset_finish = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Linear search function
def item_find(item, items):
    # Iterate through each element in the list
    for x in range(0, len(items)):
        # If a matching element is found
        if items[x] == item:
            # Return the index of the element
            return x
    # If no match is found, return None
    return None

# Binary search function
def binary_search(item, items):
    # Determine the size of the list
    list_size = len(items) - 1
    # Initialize the indices of the first and last elements
    first = 0
    last = list_size

    # Use binary search algorithm
    while first <= last:
        # Calculate the index of the middle element
        mid = (first + last) // 2
        # If the searched item is equal to the middle element, return its index
        if item == items[mid]:
            return mid
        # If the searched item is greater than the middle element, update the first pointer
        if item > items[mid]:
            first = mid + 1
        else:
            # Otherwise, update the last pointer
            last = mid - 1

    # If first is greater than last, it means no match was found, so return None
    if first > last:
        return None

# Search for elements in the sorted dataset

# Use linear search to find element 87
print("Linear Search Result (item_find):")
result_linear = item_find(87, dataset_finish)
print(result_linear)

# Use binary search to find element 9
print("Binary Search Result (binary_search):")
result_binary = binary_search(9, dataset_finish)
print(result_binary)
