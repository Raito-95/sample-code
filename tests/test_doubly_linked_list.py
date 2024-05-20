import pytest
from DataStructures.doubly_linked_list import DoublyLinkedList


@pytest.fixture
def dll():
    dll = DoublyLinkedList()
    for num in [1, 2, 3]:
        dll.append(num)
    return dll


def test_append_and_display(dll):
    dll.append(4)
    assert dll.display_forward() == [1, 2, 3, 4]
    assert dll.display_backward() == [4, 3, 2, 1]


def test_delete(dll):
    node = dll.find(2)
    dll.delete(node)
    assert dll.display_forward() == [1, 3]


def test_find(dll):
    node = dll.find(3)
    assert node.data == 3
