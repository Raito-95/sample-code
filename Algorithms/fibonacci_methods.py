def fibonacci_recursive(n, memo=None):
    """
    Recursively calculates the nth Fibonacci number using memoization to improve efficiency.
    Args:
        n (int): The position in the Fibonacci sequence.
        memo (dict, optional): A dictionary used to store previously calculated Fibonacci numbers to
        avoid redundant calculations.

    Returns:
        int: The nth Fibonacci number.
    """
    if memo is None:
        memo = {}
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n in memo:
        return memo[n]
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        result = fibonacci_recursive(n - 1, memo) + fibonacci_recursive(n - 2, memo)
        memo[n] = result
        return result


def fibonacci_iterative(n):
    """
    Iteratively calculates the nth Fibonacci number.
    Args:
        n (int): The position in the Fibonacci sequence.

    Returns:
        int: The nth Fibonacci number.
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    fib = [0, 1]
    for i in range(2, n + 1):
        fib.append(fib[i - 1] + fib[i - 2])
    return fib[n]


def main():
    # Test the function with valid and invalid inputs
    test_cases = [-1, 0, 1, 10]
    for case in test_cases:
        try:
            print(
                f"Fibonacci {case}: Recursive: {fibonacci_recursive(case)}, Iterative: {fibonacci_iterative(case)}"
            )
        except ValueError as e:
            print(e)


if __name__ == "__main__":
    main()
