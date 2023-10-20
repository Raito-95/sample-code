# Define two lists of numbers
items1 = [1, 4, 7, 8, 5, 2, 3, 6, 9]
items2 = [9, 1, 2, 3, 4, 5, 6, 7, 8]

# Function: Check if a list is sorted
def is_sorted(items):
    # Use the all() function to check if the list is sorted
    return all(items[x] <= items[x + 1] for x in range(len(items) - 1))

# Function: Find the maximum value in a list
def find_max(items):
    # Base case: If the list contains only one element, it's the maximum
    if len(items) == 1:
        return items[0]

    # Recursive case: Calculate the maximum of the first element (op1) and the rest (op2)
    op1 = items[0]
    op2 = find_max(items[1:])
    print('op1:', op1)
    print('op2:', op2)

    # Compare op1 and op2, return the larger as the maximum
    if op1 > op2:
        return op1
    else:
        return op2

# Call the function and output the result
find_max(items2)
