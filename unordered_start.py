
dataset = [1, 4, 7, 8, 5, 2, 3, 6, 9]
dataset_finish = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def item_find(item, items):
    for x in range(0, len(items)):
        if items[x] == item:
            return x
    return None


def binary_search(item, items):
    list_size = len(items) - 1
    first = 0
    last = list_size

    while first <= last:
        mid = (first + last) // 2
        if item == items[mid]:
            return mid
        if item > items[mid]:
            first = mid + 1
        else:
            last = mid - 1

    if first > last:
        return None


print(binary_search(87, dataset_finish))
print(binary_search(9, dataset_finish))
