import pytest
from DataStructures.singly_linked_list import SinglyLinkedList

@pytest.fixture
def sll():
    sll = SinglyLinkedList()
    for num in [1, 2, 3]:
        sll.append(num)
    return sll

def test_append_and_display(sll):
    sll.append(4)
    assert sll.display() == [1, 2, 3, 4]

def test_delete_node(sll):
    sll.delete_node(2)
    assert sll.display() == [1, 3]

def test_search(sll):
    assert sll.search(3) is True
    assert sll.search(5) is False

def test_reverse(sll):
    sll.reverse()
    assert sll.display() == [3, 2, 1]
