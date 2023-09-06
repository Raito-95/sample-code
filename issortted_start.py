items1 = [1, 4, 7, 8, 5, 2, 3, 6, 9]
items2 = [9, 1, 2, 3, 4, 5, 6, 7, 8]


def is_sorted(items):
    # for x in range(len(items)-1):
    #     if items[x] > items[x+1]:
    #         return False
    # return True
    return all(items[x] <= items[x + 1] for x in range(len(items) - 1))


# print(is_sorted(items1))
# print(is_sorted(items2))


def find_max(items):
    if len(items) == 1:
        return items[0]

    op1 = items[0]
    op2 = find_max(items[1:])
    print('op1:', op1)
    print('op2:', op2)

    if op1 > op2:
        return op1
    else:
        return op2


find_max(items2)
