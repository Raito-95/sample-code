from Data_Structures.doubly_linked_list import DoublyLinkedList

def test_append_to_doubly_linked_list():
    dll = DoublyLinkedList()
    dll.append(1)
    dll.append(2)
    dll.append(3)

    assert dll.head.data == 1
    assert dll.head.next.data == 2
    assert dll.head.next.next.data == 3
    assert dll.head.next.next.prev.data == 2
