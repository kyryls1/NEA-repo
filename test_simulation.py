"""
PARTIAL UNIT TEST TABLE (GasSimulation/Simulation)
| Test # | Tested function                | Input data                 | Data type | Expected output                              | Predicted explanation                                     | Actual output | Pass/Fail |
|--------|--------------------------------|----------------------------|-----------|----------------------------------------------|-----------------------------------------------------------|--------------|----------|
| 1      | GasSimulation.__init__        | (0.03, 0.1, 0.005)        | Floats    | Object created with correct properties       | Should store crank_radius etc. for later logic            |              |          |
| 2      | Simulation.update_engine_load | new_load = 500            | Float     | Successfully sets engine load in crank       | Should pass the call to the crank’s update_engine_load    |              |          |
"""

import unittest
# ...existing code...
from simulation import GasSimulation, Simulation

class TestSimulation(unittest.TestCase):
    def test_gas_simulation_init(self):
        sim = GasSimulation(crank_radius=0.03, connector_rod_length=0.1, deck_clearance=0.005)
        self.assertAlmostEqual(sim.crank_radius, 0.03)
        self.assertAlmostEqual(sim.connector_rod_length, 0.1)
        self.assertAlmostEqual(sim.deck_clearance, 0.005)
        # (Predicted explanation: constructor sets essential properties)

    def test_simulation_update_engine_load(self):
        sim = Simulation(0.03, 2, 0.1, 1, 0.02, 0.05, 1, 0.002)
        sim.update_engine_load(500)
        self.assertEqual(sim.crank.engine_load, 500)
        # (Predicted explanation: call is forwarded to crank’s engine_load var)

class TestGasSimulationExtra(unittest.TestCase):
    def test_update_fuel_flow_rate(self):
        sim = GasSimulation(0.03, 0.1, 0.005)
        # ...existing code...
        sim.update_fuel_flow_rate(0.02)
        # For now, just confirm no error is raised (placeholder test)
        self.assertTrue(True)

    def test_get_temperature(self):
        sim = GasSimulation(0.03, 0.1, 0.005)
        # ...existing code...
        temp = sim.get_temperature(theta=1.0)
        self.assertIsNotNone(temp)

    def test_get_gas_moles(self):
        sim = GasSimulation(0.03, 0.1, 0.005)
        # ...existing code...
        moles = sim.get_gas_moles(theta=0.5)
        self.assertIsNotNone(moles)

    def test_get_current_deck_clearance(self):
        sim = GasSimulation(0.03, 0.1, 0.005)
        # ...existing code...
        clearance = sim.get_current_deck_clearance(piston_position=0.02)
        self.assertIsNotNone(clearance)

class TestSimulationExtra(unittest.TestCase):
    def test_toggle_starter_motor(self):
        sim = Simulation(0.03, 2, 0.1, 1, 0.02, 0.05, 1, 0.002)
        # ...existing code...
        initial = sim.crank.starter_motor_on
        sim.toggle_starter_motor()
        self.assertNotEqual(sim.crank.starter_motor_on, initial)

if __name__ == '__main__':
    unittest.main()