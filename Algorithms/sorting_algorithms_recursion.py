def bubble_sort(dataset):
    """
    Sorts a list using the bubble sort algorithm.
    Args:
        dataset (list): The list to be sorted.

    Returns:
        list: The sorted list.
    """
    n = len(dataset)
    for i in range(n - 1):
        for j in range(0, n-i-1):
            if dataset[j] > dataset[j+1]:
                dataset[j], dataset[j+1] = dataset[j+1], dataset[j]
    return dataset

def merge_sort(dataset):
    """
    Sorts a list using the merge sort algorithm with recursion.
    Args:
        dataset (list): The list to be sorted.

    Returns:
        list: The sorted list.
    """
    if len(dataset) > 1:
        mid = len(dataset) // 2
        left_half = dataset[:mid]
        right_half = dataset[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        # Merging the sorted halves
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                dataset[k] = left_half[i]
                i += 1
            else:
                dataset[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            dataset[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            dataset[k] = right_half[j]
            j += 1
            k += 1

    return dataset

def quick_sort(dataset, first, last):
    """
    Sorts a list using the quick sort algorithm with recursion.
    Args:
        dataset (list): The list to be sorted.
        first (int): The first index of the segment to be sorted.
        last (int): The last index of the segment to be sorted.

    Returns:
        list: The sorted list.
    """
    def partition(low, high):
        pivot = dataset[high]
        i = low - 1
        for j in range(low, high):
            if dataset[j] <= pivot:
                i += 1
                dataset[i], dataset[j] = dataset[j], dataset[i]
        dataset[i+1], dataset[high] = dataset[high], dataset[i+1]
        return i+1

    if first < last:
        pi = partition(first, last)
        quick_sort(dataset, first, pi-1)
        quick_sort(dataset, pi+1, last)

    return dataset

def main():
    """
    Main function to demonstrate the functionality of sorting algorithms.
    """
    dataset = [3, 6, 8, 10, 1, 2, 1, 9, 5, 7]
    print("Original dataset:", dataset)
    print("Bubble sorted:", bubble_sort(dataset.copy()))
    print("Merge sorted:", merge_sort(dataset.copy()))
    print("Quick sorted:", quick_sort(dataset.copy(), 0, len(dataset) - 1))

if __name__ == "__main__":
    main()
