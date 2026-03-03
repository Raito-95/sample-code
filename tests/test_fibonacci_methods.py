import pytest
from core.algorithms.fibonacci_methods import fibonacci_recursive, fibonacci_iterative


def test_fibonacci_recursive():
    assert fibonacci_recursive(0) == 0
    assert fibonacci_recursive(1) == 1
    assert fibonacci_recursive(10) == 55
    assert fibonacci_recursive(5) == 5


def test_fibonacci_iterative():
    assert fibonacci_iterative(0) == 0
    assert fibonacci_iterative(1) == 1
    assert fibonacci_iterative(10) == 55
    assert fibonacci_iterative(5) == 5


def test_fibonacci_negative():
    with pytest.raises(ValueError):
        fibonacci_recursive(-1)
    with pytest.raises(ValueError):
        fibonacci_iterative(-1)

