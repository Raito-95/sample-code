# Recursive function example
def recursive(x):
    if x == 0:
        print('Done')
        return
    else:
        print(x)
        recursive(x - 1)
        print('x:', x)

# Bubble sort
def bubble_sort(dataset):
    for x in range(len(dataset) - 1, 0, -1):
        for y in range(x):
            if dataset[y] > dataset[y + 1]:
                temp = dataset[y]
                dataset[y] = dataset[y + 1]
                dataset[y + 1] = temp
        print(f'Dataset: {dataset}')

# Merge sort
def merge_sort(dataset):
    if len(dataset) > 1:
        mid = len(dataset) // 2
        left_arr = dataset[:mid]
        right_arr = dataset[mid:]

        merge_sort(left_arr)
        merge_sort(right_arr)
        x = 0  # Left
        y = 0  # Right
        z = 0  # Output

        # When both left and right arrays have elements
        while len(left_arr) > x and len(right_arr) > y:
            if left_arr[x] > right_arr[y]:
                dataset[z] = right_arr[y]
                y += 1
            else:
                dataset[z] = left_arr[x]
                x += 1
            z += 1

        while len(left_arr) > x:
            dataset[z] = left_arr[x]
            x += 1
            z += 1

        while len(right_arr) > y:
            dataset[z] = right_arr[y]
            y += 1
            z += 1

    return dataset

# Quick sort
def quick_sort(first, last, dataset):
    if last > first:
        pivot = partition(first, last, dataset)

        quick_sort(first, pivot - 1, dataset)
        quick_sort(pivot + 1, last, dataset)

    return dataset

# Partition function
def partition(first, last, dataset):
    pivot = dataset[first]

    right_move = first + 1
    left_move = last

    done = False
    while not done:
        if right_move <= left_move and dataset[right_move] <= pivot:
            right_move += 1
        if left_move >= right_move and dataset[left_move] >= pivot:
            left_move -= 1
        if right_move > left_move:
            done = True
        else:
            temp = dataset[right_move]
            dataset[right_move] = dataset[left_move]
            dataset[left_move] = temp

    temp = dataset[first]
    dataset[first] = dataset[left_move]
    dataset[left_move] = temp

    return left_move

# Main function
def main():
    dataset = [1, 4, 7, 8, 5, 2, 3, 6, 9]
    result = quick_sort(0, len(dataset) - 1, dataset)
    print(result)

if __name__ == "__main__":
    main()
