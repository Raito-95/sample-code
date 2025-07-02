from Algorithms.dynamic_programming import knapsack, longest_common_subsequence


def test_knapsack():
    values = [60, 100, 120]
    weights = [10, 20, 30]
    assert knapsack(values, weights, 50) == 220
    assert knapsack(values, weights, 0) == 0


def test_longest_common_subsequence():
    assert longest_common_subsequence('ABCBDAB', 'BDCABA') == 'BCBA'
    assert longest_common_subsequence('', 'ABC') == ''
