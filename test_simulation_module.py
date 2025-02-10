import math
import pytest
from simulation import Simulation

TEST_DT = 0.001
PARAMETERS = {
    'crank_radius': 0.05,
    'crank_mass': 5,
    'connecting_rod_length': 0.1,
    'rod_mass': 2,
    'piston_radius': 0.04,
    'piston_mass': 3,
    'piston_length': 0.06,
    'deck_clearance': 0.001
}

@pytest.fixture
def test_simulation():
    simulation = Simulation(*PARAMETERS.values())
    return simulation

def test_update_simulation_with_no_angular_velocityy(test_simulation):
    """Test simulation update with zero initial angular velocity."""
    initial_angle = test_simulation.crank.angle_radians
    
    test_simulation.update_all(TEST_DT)
    
    assert math.isclose(test_simulation.crank.current_torque, 0, abs_tol=1e-15)
    assert math.isclose(test_simulation.crank.angular_velocity, 0, abs_tol=1e-15)
    assert math.isclose(test_simulation.crank.angle_radians, initial_angle, abs_tol=1e-15)
    assert math.isclose(test_simulation.piston.velocity, 0, abs_tol=1e-15)

def test_update_simulation_positive_angular_velocity(test_simulation):
    """Test simulation update with positive angular velocity and set fuel flow rate."""
    test_simulation.crank.angular_velocity = 2
    test_simulation.gas_simulation.decompression_valve_open = False
    test_simulation.crank.angle_radians = math.pi / 4

    assert test_simulation.gas_simulation.moles_before_combustion == 0
    test_simulation.update_fuel_flow_rate(0.04)
    assert math.isclose(test_simulation.gas_simulation.moles_before_combustion, 54/11423, abs_tol=1e-15)

    test_simulation.update_all(TEST_DT)

    assert math.isclose(test_simulation.crank.angle_radians, 1.137178324070126, abs_tol=1e-15)
    assert math.isclose(test_simulation.piston.position.y, 0.14544275951693694, abs_tol=1e-15)
    assert math.isclose(test_simulation.crank.current_torque, 2186.1260042042372, abs_tol=1e-15)

def test_starter_motor_behavior(test_simulation):
    """Test starter motor activation and deactivation."""
    
    assert test_simulation.crank.starter_motor_on is False
    test_simulation.toggle_starter_motor()
    assert test_simulation.crank.starter_motor_on is True

    test_simulation.update_all(TEST_DT)
    assert test_simulation.crank.current_torque == test_simulation.crank.STARTER_MOTOR_TORQUE
    assert math.isclose(test_simulation.crank.angular_velocity, 3.2, abs_tol=1e-15)

    test_simulation.toggle_starter_motor()
    assert test_simulation.crank.starter_motor_on is False
