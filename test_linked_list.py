"""
PARTIAL UNIT TEST TABLE (LinkedList)
| Test # | Tested function  | Input data                 | Data type | Expected output                              | Predicted explanation                                   | Actual output | Pass/Fail |
|--------|------------------|----------------------------|-----------|----------------------------------------------|---------------------------------------------------------|--------------|----------|
| 1      | append           | Data = 42                 | Integer   | LinkedList size increases by 1, tail = 42    | The append method should link a new node at the end.    |              |          |
| 2      | __len__ (length) | - (after some appends)    | -         | Correct integer length of the linked list    | Should return expected list size, ignoring any extras.   |              |          |
"""

import unittest
# ...existing code...
from linked_list import LinkedList

class TestLinkedList(unittest.TestCase):
    def test_append_and_len(self):
        ll = LinkedList()
        self.assertEqual(len(ll), 0)    # initially empty
        ll.append(42)
        self.assertEqual(len(ll), 1)    # size should now be 1
        ll.append(100)
        self.assertEqual(len(ll), 2)    # size should now be 2
        # (Predicted explanation: LinkedList grows with each append)

    def test_iter(self):
        ll = LinkedList()
        data_items = [10, 20, 30]
        for item in data_items:
            ll.append(item)
        collected = [val for val in ll] # test __iter__
        self.assertListEqual(collected, data_items)
        # (Predicted explanation: iteration traverses all appended nodes)

if __name__ == '__main__':
    unittest.main()