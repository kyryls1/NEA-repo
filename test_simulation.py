from simulation import Simulation
from vector import Vector
import math

# Test toggle_starter_motor
test_simulation = Simulation(0.04, 6, 0.08, 0.5, 0.045, 1.5, 0.05, 0.001)
assert test_simulation.crank.starter_motor_on == False
print(test_simulation.crank.starter_motor_on)
test_simulation.toggle_starter_motor()
assert test_simulation.crank.starter_motor_on == True
print(test_simulation.crank.starter_motor_on)
test_simulation.toggle_starter_motor()
assert test_simulation.crank.starter_motor_on == False
print(test_simulation.crank.starter_motor_on)
print("Unit Test Passed")

# Test calculate_velocity_gradient with zero velocity
test_simulation = Simulation(0.04, 6, 0.08, 0.5, 0.045, 1.5, 0.05, 0.001)
gradient = test_simulation.calculate_velocity_gradient(0, 1e-6, -2.5)
assert gradient == 0
print(gradient)
print("Unit Test Passed")

# Test calculate_velocity_gradient with positive velocity
gradient = test_simulation.calculate_velocity_gradient(2, 1e-6, -2.5)
assert gradient == -5e12
print(gradient)
print("Unit Test Passed")

# Test calculate_velocity_gradient with negative velocity
gradient = test_simulation.calculate_velocity_gradient(-2, 1e-6, -2.5)
assert gradient == 5e12
print(gradient)
print("Unit Test Passed")

# Test skirt calculate_velocity_gradient with negative velocity
gradient = test_simulation.calculate_velocity_gradient(2, 1e-6, -2.1)
assert math.isclose(gradient, -4.2e12, abs_tol=1e-15)
print(gradient)
print("Unit Test Passed")

# Test find_normal_to_crank_motion at 0
test_simulation = Simulation(0.04, 6, 0.08, 0.5, 0.045, 1.5, 0.05, 0.001)
normal = test_simulation.find_normal_to_crank_motion(0)
assert math.isclose(normal.x, 1, abs_tol=1e-15)
assert math.isclose(normal.y, 0, abs_tol=1e-15)
print(normal.x, normal.y)
print("Unit Test Passed")

# Test find_normal_to_crank_motion at pi/2
normal = test_simulation.find_normal_to_crank_motion(math.pi/2)
assert math.isclose(normal.x, 0, abs_tol=1e-15)
assert math.isclose(normal.y, 1, abs_tol=1e-15)
print(normal.x, normal.y)
print("Unit Test Passed")

# Test find_normal_to_crank_motion at pi/4
normal = test_simulation.find_normal_to_crank_motion(math.pi/4)
assert math.isclose(normal.x, 1, abs_tol=1e-15)
assert math.isclose(normal.y, 1, abs_tol=1e-15)
print(normal.x, normal.y)
print("Unit Test Passed")

# Test transfer_force_to_rod with vertical rod direction
test_simulation = Simulation(0.04, 6, 0.08, 0.5, 0.045, 1.5, 0.05, 0.001)
rod_direction = Vector(0, 1)
force = test_simulation.transfer_force_to_rod(10, rod_direction)
assert math.isclose(force, 10, abs_tol=1e-15)
print(force)
print("Unit Test Passed")

# Test transfer_force_to_rod with rod direction left of vertical
rod_direction = Vector(-0.5, 1)  # ~27 degrees from vertical
force = test_simulation.transfer_force_to_rod(10, rod_direction)
assert math.isclose(force, 11.180339887498949, abs_tol=1e-15)
print(force)
print("Unit Test Passed")

# Test transfer_force_to_rod with rod direction right of vertical
rod_direction = Vector(0.5, 1)  # ~27 degrees from vertical
force = test_simulation.transfer_force_to_rod(10, rod_direction)
assert math.isclose(force, 11.180339887498949, abs_tol=1e-15)  # 10/cos(27°)
print(force)
print("Unit Test Passed")

# Test transfer_force_to_rod with zero force
rod_direction = Vector(0.5, 1)
force = test_simulation.transfer_force_to_rod(0, rod_direction)
assert math.isclose(force, 0, abs_tol=1e-15)
print(force)
print("Unit Test Passed")

# Test transfer_force_to_rod with negative force
rod_direction = Vector(0.5, 1)
force = test_simulation.transfer_force_to_rod(-10, rod_direction)
assert math.isclose(force, -11.180339887498949, abs_tol=1e-15)
print(force)
print("Unit Test Passed")
