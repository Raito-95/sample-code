"""Dynamic programming algorithm implementations."""


def knapsack(values, weights, capacity):
    """Solve the 0/1 knapsack problem using dynamic programming.

    Args:
        values (list[int]): Value of each item.
        weights (list[int]): Weight of each item.
        capacity (int): Maximum weight capacity of the knapsack.

    Returns:
        int: The maximum value achievable within the given capacity.
    """
    n = len(values)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i - 1][w], values[i - 1] + dp[i - 1][w - weights[i - 1]])
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][capacity]


def longest_common_subsequence(s1, s2):
    """Return the longest common subsequence of two strings.

    Args:
        s1 (str): First string.
        s2 (str): Second string.

    Returns:
        str: The longest common subsequence between ``s1`` and ``s2``.
    """
    m, n = len(s1), len(s2)
    dp = [[""] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + s1[i - 1]
            else:
                dp[i][j] = dp[i - 1][j] if len(dp[i - 1][j]) >= len(dp[i][j - 1]) else dp[i][j - 1]
    return dp[m][n]


if __name__ == "__main__":
    print("Knapsack sample:")
    vals = [60, 100, 120]
    wts = [10, 20, 30]
    print("Max value:", knapsack(vals, wts, 50))

    print("LCS sample:")
    print(longest_common_subsequence("ABCBDAB", "BDCABA"))
