
# recursive
def fibonacci_recursive(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# 計算前 10 個斐波那契數
for i in range(10):
    print(fibonacci_recursive(i))


# iterative
def fibonacci_iterative(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        fib = [0, 1]
        for i in range(2, n + 1):
            fib.append(fib[i - 1] + fib[i - 2])
        return fib[n]

# 計算前 10 個斐波那契數
for i in range(10):
    print(fibonacci_iterative(i))