# Recursive way to calculate the Fibonacci sequence
def fibonacci_recursive(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# Calculate the first 10 Fibonacci numbers
for i in range(10):
    print(fibonacci_recursive(i))

# Iterative way to calculate the Fibonacci sequence
def fibonacci_iterative(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        fib = [0, 1]
        for i in range(2, n + 1):
            fib.append(fib[i - 1] + fib[i - 2])
        return fib[n]

# Calculate the first 10 Fibonacci numbers using iteration
for i in range(10):
    print(fibonacci_iterative(i))
