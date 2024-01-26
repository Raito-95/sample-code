import pytest
from Algorithms.fibonacci_calculator import fibonacci_recursive, fibonacci_iterative

@pytest.mark.parametrize("test_input,expected", [
    (0, 0),
    (1, 1),
    (5, 5),
    (10, 55)
])
def test_fibonacci_recursive(test_input, expected):
    assert fibonacci_recursive(test_input) == expected

@pytest.mark.parametrize("test_input,expected", [
    (0, 0),
    (1, 1),
    (5, 5),
    (10, 55)
])
def test_fibonacci_iterative(test_input, expected):
    assert fibonacci_iterative(test_input) == expected
