from linked_list import LinkedList, Node

"""
test_node = Node(None)
assert test_node.data == None
assert test_node.next == None
print(test_node.data)
print(test_node.next)
print("Unit test passed")

test_linked_list = LinkedList()
assert test_linked_list.head == None
assert test_linked_list.tail == None
assert test_linked_list.size == 0
print(test_linked_list.head)
print(test_linked_list.tail)
print(test_linked_list.size)
print("Unit test passed")
"""

test_linked_list = LinkedList()
test_linked_list.append(1)
test_linked_list.append(2)
assert test_linked_list.head.data == 1
assert test_linked_list.tail.data == 2
assert test_linked_list.tail.next == None
assert test_linked_list.head.next == test_linked_list.tail
assert test_linked_list.size == 2
print(test_linked_list.head.data)
print(test_linked_list.head.next)
print(test_linked_list.size)
print("Unit test passed")