"""
PARTIAL UNIT TEST TABLE (SimulationWindow)
| Test # | Tested function       | Input data     | Data type | Expected output                    | Predicted explanation                                  | Actual output | Pass/Fail |
|--------|-----------------------|----------------|-----------|------------------------------------|--------------------------------------------------------|--------------|----------|
| 1      | mm_to_m              | value=50       | Integer   | Returns 0.05                       | Convert mm to m by dividing by 1000                    |              |          |
| 2      | validate_parameter   | param='fuel_flow', val=0.5 | Mixed | Accepts 0.5, returns True         | 0.5 is within 'fuel_flow' constraints [0, 1]           |              |          |
"""

import unittest
# ...existing code...
from main import SimulationWindow

class TestSimulationWindow(unittest.TestCase):
    def setUp(self):
        self.window = SimulationWindow(width=800, height=600)

    def test_mm_to_m(self):
        result = self.window.mm_to_m(50)
        self.assertEqual(result, 0.05)
        # (Predicted explanation: divides by 1000)

    def test_validate_parameter(self):
        is_valid = self.window.validate_parameter('fuel_flow', 0.5)
        self.assertTrue(is_valid)
        # (Predicted explanation: 0.5 within [0,1])

class TestSimulationWindowExtra(unittest.TestCase):
    def test_ignition_starter_button(self):
        window = SimulationWindow(width=800, height=600)
        # Suppose we set up a simulation with blank parameters
        window.start_simulation([30, 2, 100, 1, 20, 30, 5, 1], window.origin)
        # ...existing code...
        was_stalled = window.engine_stalled
        window.ignition_starter_button()
        # Just verify the state changed
        self.assertNotEqual(window.engine_stalled, was_stalled)

if __name__ == '__main__':
    unittest.main()