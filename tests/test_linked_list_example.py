from Data_Structures.linked_list_example import LinkedList

def test_append_to_linked_list():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)

    assert ll.head.data == 1
    assert ll.head.next.data == 2
    assert ll.head.next.next.data == 3
