from Data_Structures.stack_example import Stack

def test_stack_operations():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)

    assert stack.peek() == 3
    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.is_empty()
