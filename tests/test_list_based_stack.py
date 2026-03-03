import pytest
from core.data_structures.list_based_stack import Stack


@pytest.fixture
def stack():
    st = Stack()
    for num in [1, 2, 3]:
        st.push(num)
    return st


def test_push(stack):
    stack.push(4)
    assert stack.peek() == 4
    assert stack.size() == 4


def test_pop(stack):
    assert stack.pop() == 3
    assert stack.peek() == 2


def test_is_empty(stack):
    stack.pop()
    stack.pop()
    stack.pop()
    assert stack.is_empty() is True

