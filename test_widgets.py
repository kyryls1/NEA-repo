
"""
PARTIAL UNIT TEST TABLE (widgets)
| Test # | Tested function         | Input data    | Data type | Expected output                | Predicted explanation                                       | Actual output | Pass/Fail |
|--------|-------------------------|---------------|-----------|--------------------------------|-------------------------------------------------------------|--------------|----------|
| 1      | TextBox.is_mouseover   | x=50, y=70    | Integers  | True if widget covers (50,70)  | Should detect pointer position is inside the bounding box   |              |          |
"""

import unittest
import widgets

class MockBatch:
    pass

class TestWidgets(unittest.TestCase):
    def test_textbox_mouseover(self):
        textbox = widgets.TextBox("Test:", 40, 60, 100, batch=MockBatch())
        # x-range: 40->140, y-range: 60->(60+some default height)
        self.assertTrue(textbox.is_mouseover(50,70))
        # (Predicted explanation: 50,70 is inside the bounding box)

if __name__ == '__main__':
    unittest.main()