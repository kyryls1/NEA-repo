"""
PARTIAL UNIT TEST TABLE (Renderer)
| Test # | Tested function           | Input data               | Data type | Expected output                            | Predicted explanation                                    | Actual output | Pass/Fail |
|--------|---------------------------|--------------------------|-----------|--------------------------------------------|----------------------------------------------------------|--------------|----------|
| 1      | render                   | crank.angle_radians=0.5 | Float     | Some rotation changes for shapes           | Should rotate lines/circles and update their positions   |              |          |
| 2      | store_graph_point        | (time=1.0, torque=20)   | Mixed     | Graph points list size increments by 1     | Adds a tuple to self.graph_points                        |              |          |
"""

import unittest
import math
# ...existing code...
from renderer import Renderer
from vector import Vector
from mechanical_components import Crank, ConnectorRod, Piston

class MockBatch:
    pass

class TestRenderer(unittest.TestCase):
    def test_render_rotation(self):
        renderer = Renderer(batch=MockBatch(), origin=Vector(0,0),
                            crank_radius_m=0.02, rod_length_m=0.05,
                            piston_radius_m=0.01, piston_length_m=0.02)
        crank = Crank(radius=0.02, mass=2)
        rod = ConnectorRod(1, 0.05, 0.02)
        piston = Piston(1, 0.01, 0.02, 0.001, 0.02)
        crank.angle_radians = 0.5
        renderer.render(crank, rod, piston)
        # (Predicted explanation: The shapes’ rotation/positions updated accordingly)

    def test_store_graph_point(self):
        renderer = Renderer(batch=MockBatch(), origin=Vector(0,0),
                            crank_radius_m=0.02, rod_length_m=0.05,
                            piston_radius_m=0.01, piston_length_m=0.02)
        initial_length = len(renderer.graph_points)
        renderer.store_graph_point(1.0, 20, 300)
        self.assertEqual(len(renderer.graph_points), initial_length + 1)
        # (Predicted explanation: new tuple is appended to graph_points)

class TestRendererStorage(unittest.TestCase):
    def test_store_paused_point(self):
        renderer = Renderer(batch=None, origin=Vector(0,0), crank_radius_m=0.02, rod_length_m=0.05,
                            piston_radius_m=0.01, piston_length_m=0.02)
        initial_len = len(renderer.paused_points)
        renderer.store_paused_point(10.5)
        self.assertEqual(len(renderer.paused_points), initial_len + 1)

    def test_store_throttle_change_point(self):
        renderer = Renderer(batch=None, origin=Vector(0,0), crank_radius_m=0.02, rod_length_m=0.05,
                            piston_radius_m=0.01, piston_length_m=0.02)
        initial_len = len(renderer.throttle_change_points)
        renderer.store_throttle_change_point(2.0, 0.5)
        self.assertEqual(len(renderer.throttle_change_points), initial_len + 1)

    def test_store_engine_load_change_point(self):
        renderer = Renderer(batch=None, origin=Vector(0,0), crank_radius_m=0.02, rod_length_m=0.05,
                            piston_radius_m=0.01, piston_length_m=0.02)
        initial_len = len(renderer.engine_load_change_points)
        renderer.store_engine_load_change_point(3.0, 250)
        self.assertEqual(len(renderer.engine_load_change_points), initial_len + 1)

if __name__ == '__main__':
    unittest.main()