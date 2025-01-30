"""
PARTIAL UNIT TEST TABLE (Crank/ConnectorRod/Piston)
| Test # | Tested function            | Input data                  | Data type | Expected output                   | Predicted explanation                                    | Actual output | Pass/Fail |
|--------|----------------------------|-----------------------------|-----------|-----------------------------------|----------------------------------------------------------|--------------|----------|
| 1      | Crank.update              | force=10, dt=0.1           | Floats    | Increases angular_velocity        | Should increment angular velocity based on torque        |              |          |
| 2      | ConnectorRod.update       | delta_theta = pi/6         | Float     | rod_end.y changed appropriately   | Should compute new piston anchor position                |              |          |
| 3      | Piston.update_velocity    | dt=0.1                     | Float     | velocity updated correctly        | Should recalc velocity from change in position           |              |          |
"""

import unittest
import math
# ...existing code...
from mechanicalComponents import Crank, ConnectorRod, Piston
from vector import Vector

class TestMechanicalComponents(unittest.TestCase):
    def test_crank_update(self):
        crank = Crank(radius=0.05, mass=2)
        initial_omega = crank.angular_velocity
        crank.update(force=10, dt=0.1)
        self.assertNotEqual(crank.angular_velocity, initial_omega)
        # (Predicted explanation: torque -> angular accel -> new velocity)

    def test_connector_rod_update(self):
        rod = ConnectorRod(mass=1, length=0.1, crank_radius_offset=0.05)
        initial_piston_y = rod.rod_end.y
        rod.update(delta_theta=math.pi/6)
        self.assertNotEqual(rod.rod_end.y, initial_piston_y)
        # (Predicted explanation: rod_end moves from rotation + geometry)

    def test_piston_update_velocity(self):
        piston = Piston(mass=1, radius=0.02, length=0.05, deck_clearance=0.001, rod_offset=0)
        piston.position.y = 0.05
        piston.update_velocity(dt=0.1)
        self.assertNotEqual(piston.velocity, 0.0)
        # (Predicted explanation: velocity updated based on new position)

class TestCrankAdditional(unittest.TestCase):
    def test_calculate_torque(self):
        crank = Crank(radius=0.05, mass=2)
        t = crank.calculate_torque(10)
        self.assertEqual(t, 0.5)

    def test_subtract_engine_load(self):
        crank = Crank(radius=0.05, mass=2)
        crank.engine_load = 50
        torque_after_load = crank.subtract_engine_load(100, 0.0)
        self.assertNotEqual(torque_after_load, 100)
    
    def test_calculate_delta_theta(self):
        crank = Crank(radius=0.05, mass=2)
        crank.angular_velocity = 10
        delta = crank.calculate_delta_theta(0.1)
        self.assertAlmostEqual(delta, 1.0)  # 10 rad/s * 0.1s

class TestPistonExtra(unittest.TestCase):
    def test_piston_update(self):
        piston = Piston(mass=1, radius=0.02, length=0.05, deck_clearance=0.001, rod_offset=0)
        initial_y = piston.position.y
        piston.update(0.07, dt=0.1)
        self.assertNotEqual(piston.position.y, initial_y)
        self.assertNotEqual(piston.velocity, 0)

if __name__ == '__main__':
    unittest.main()