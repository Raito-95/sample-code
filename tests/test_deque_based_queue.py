import pytest
from core.data_structures.deque_based_queue import Queue


@pytest.fixture
def queue():
    q = Queue()
    for num in [1, 2, 3]:
        q.enqueue(num)
    return q


def test_enqueue(queue):
    queue.enqueue(4)
    assert queue.peek() == 1
    assert queue.size() == 4


def test_dequeue(queue):
    assert queue.dequeue() == 1
    assert queue.peek() == 2


def test_is_empty(queue):
    queue.dequeue()
    queue.dequeue()
    queue.dequeue()
    assert queue.is_empty() is True

