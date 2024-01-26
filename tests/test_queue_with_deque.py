from Data_Structures.queue_with_deque import Queue

def test_queue_operations():
    queue = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)

    assert queue.dequeue() == 1
    assert queue.dequeue() == 2
    assert queue.size() == 1
    assert not queue.is_empty()
    assert queue.dequeue() == 3
    assert queue.is_empty()
