
def recursive(x):
    if x == 0:
        print('Done')
        return
    else:
        print(x)
        recursive(x-1)
        print('x:', x)


def bubble_start(dataset):
    for x in range(len(dataset) - 1, 0, -1):
        for y in range(x):
            if dataset[y] > dataset[y+1]:
                temp = dataset[y]
                dataset[y] = dataset[y+1]
                dataset[y+1] = temp
        print(f'dataset: {dataset}')


def mergesort(dataset):
    if len(dataset) > 1:
        mid = len(dataset) // 2
        left_arr = dataset[:mid]
        right_arr = dataset[mid:]

        mergesort(left_arr)
        mergesort(right_arr)
        x = 0  # left
        y = 0  # right
        z = 0  # output

        # 左右都還有數值的情況
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


def quicksort(first, last, dataset):
    if last > first:
        volume = partition(first, last, dataset)

        quicksort(first, volume-1, dataset)
        quicksort(volume+1, last, dataset)

    return dataset


def partition(first, last, dataset):
    volume = dataset[first]

    right_move = first + 1
    left_move = last

    done = False
    while not done:
        if right_move <= left_move and dataset[right_move] <= volume:
            right_move += 1
        if left_move >= right_move and dataset[left_move] >= volume:
            left_move -= 1
        if right_move > left_move:
            done = True
        else:
            tmp = dataset[right_move]
            dataset[right_move] = dataset[left_move]
            dataset[left_move] = tmp

    tmp = dataset[first]
    dataset[first] = dataset[left_move]
    dataset[left_move] = tmp

    return left_move


def main():
    dataset = [1, 4, 7, 8, 5, 2, 3, 6, 9]
    result = quicksort(0, len(dataset)-1, dataset)
    print(result)


if __name__ == "__main__":
    main()
