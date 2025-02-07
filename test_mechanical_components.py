from mechanical_components import Crank, Piston
import math

# Comment out existing Crank tests
'''
# Test initialization with expected values
test_crank = Crank(0.04, 6)
assert test_crank.radius == 0.04
assert test_crank.mass == 6
assert math.isclose(test_crank.moment_of_inertia, 0.0048, abs_tol=1e-15)
assert test_crank.engine_load == 0
assert test_crank.starter_motor_on == False
assert test_crank.angular_velocity == 0
assert test_crank.angle_radians == 0
assert test_crank.current_torque == 0
print(test_crank.radius, test_crank.mass, test_crank.moment_of_inertia, test_crank.engine_load, 
      test_crank.starter_motor_on, test_crank.angular_velocity, test_crank.angle_radians, test_crank.current_torque)
print("Unit Test Passed")

# Test update_engine_load
test_crank = Crank(0.04, 6)
test_crank.update_engine_load(100)
assert test_crank.engine_load == 100
print(test_crank.engine_load)
print("Unit Test Passed")

# Test calculate_torque
test_crank = Crank(0.04, 6)
torque = test_crank.calculate_torque(100)
assert torque == 4
print(torque)
print("Unit Test Passed")

# Test calculate_delta_theta
test_crank = Crank(0.04, 6)
test_crank.angular_velocity = 10
delta_theta = test_crank.calculate_delta_theta(0.1)
assert delta_theta == 1
print(delta_theta)
print("Unit Test Passed")

# Test update_angle
test_crank = Crank(0.04, 6)
# Test with angle < 2π
test_crank.update_angle(math.pi)
assert test_crank.angle_radians == math.pi
print(test_crank.angle_radians)
# Test with angle >= 2π
test_crank.update_angle(math.pi)
assert test_crank.angle_radians == 0
print(test_crank.angle_radians)
print("Unit Test Passed")

# Test update_angular_velocity
test_crank = Crank(0.05, 5)
test_crank.update_angular_velocity(0, 0.1)
assert test_crank.angular_velocity == 0
print(test_crank.angular_velocity)
print("Unit Test Passed")

# Test with positive torque
test_crank = Crank(0.05, 5)
test_crank.update_angular_velocity(12.5, 0.1)
assert math.isclose(test_crank.angular_velocity, 200, abs_tol=1e-15)
print(test_crank.angular_velocity)
print("Unit Test Passed")

# Test with negative torque
test_crank = Crank(0.05, 5)
test_crank.update_angular_velocity(-12.5, 0.1)
assert math.isclose(test_crank.angular_velocity, -200, abs_tol=1e-15)
print(test_crank.angular_velocity)
print("Unit Test Passed")

# Test subtract_engine_load
test_crank = Crank(0.04, 6)
test_crank.engine_load = 100
torque = test_crank.subtract_engine_load(10)
assert torque == 10
print(torque)
print("Unit Test Passed")

# Test with non-zero angular velocity and engine load
test_crank = Crank(0.04, 6)
test_crank.angular_velocity = 10
test_crank.engine_load = 100
torque = test_crank.subtract_engine_load(10)
assert torque == 0
print(torque)
print("Unit Test Passed")

# Test get_rpm
test_crank = Crank(0.04, 6)
test_crank.angular_velocity = 2 * math.pi
rpm = test_crank.get_rpm()
assert math.isclose(rpm, 60, abs_tol=1e-15)
print(rpm)
print("Unit Test Passed")


from mechanical_components import ConnectingRod
from vector import Vector
import math

# Test ConnectingRod initialization
test_rod = ConnectingRod(0.5, 0.08, 0.04)
assert test_rod.mass == 0.5
assert test_rod.length_squared == 0.0064
assert test_rod.crank_anchor.x == 0
assert test_rod.crank_anchor.y == 0.04
assert test_rod.piston_anchor.x == 0
assert test_rod.piston_anchor.y == 0.12
print(test_rod.mass, test_rod.length_squared, test_rod.crank_anchor.x, test_rod.crank_anchor.y, test_rod.piston_anchor.x, test_rod.piston_anchor.y)
print("Unit Test Passed")

# Test update_crank_anchor_position with zero rotation
test_rod = ConnectingRod(0.5, 0.08, 0.04)
test_rod.update_crank_anchor_position(0)
assert test_rod.crank_anchor.x == 0
assert test_rod.crank_anchor.y == 0.04
print(test_rod.crank_anchor.x, test_rod.crank_anchor.y)
print("Unit Test Passed")

# Test update_crank_anchor_position with PI/2 rotation
test_rod = ConnectingRod(0.5, 0.08, 0.04)
test_rod.update_crank_anchor_position(math.pi/2)
assert math.isclose(test_rod.crank_anchor.x, 0.04, abs_tol=1e-15)
assert math.isclose(test_rod.crank_anchor.y, 0, abs_tol=1e-15)
print(test_rod.crank_anchor.x, test_rod.crank_anchor.y)
print("Unit Test Passed")

# Test update_piston_anchor_position with no horizontal displacement
test_rod = ConnectingRod(0.5, 0.08, 0.04)
test_rod.update_piston_anchor_position()
assert test_rod.piston_anchor.x == 0
assert test_rod.piston_anchor.y == 0.12
print(test_rod.piston_anchor.x, test_rod.piston_anchor.y)
print("Unit Test Passed")

# Test update_piston_anchor_position with angled rod
test_rod = ConnectingRod(0.5, 0.08, 0.04)
test_rod.crank_anchor.x = 0.04
test_rod.crank_anchor.y = 0.00
test_rod.update_piston_anchor_position()
assert math.isclose(test_rod.piston_anchor.x, 0, abs_tol=1e-15)
assert math.isclose(test_rod.piston_anchor.y, 0.0692820323, abs_tol=1e-15)
print(test_rod.piston_anchor.x, test_rod.piston_anchor.y)
print("Unit Test Passed")
'''
# Test Piston initialization
test_piston = Piston(1.5, 0.045, 0.05, 0.001, 0.12)
assert test_piston.mass == 1.5
assert test_piston.radius == 0.045
assert test_piston.length == 0.05
assert test_piston.deck_clearance == 0.001
assert math.isclose(test_piston.surface_area, 4.5e-3 * math.pi, abs_tol=1e-15)
assert test_piston.position.x == 0
assert test_piston.position.y == 0.12
assert test_piston.last_position.x == 0
assert test_piston.last_position.y == 0.12
assert test_piston.velocity == 0
print(test_piston.mass, test_piston.radius, test_piston.length, test_piston.deck_clearance, 
      test_piston.surface_area, test_piston.position.x, test_piston.position.y, test_piston.last_position.x, 
      test_piston.last_position.y, test_piston.velocity)
print("Unit Test Passed")

# Test update with no y change
test_piston = Piston(1.5, 0.045, 0.05, 0.001, 0.12)
test_piston.update(0.12, 0.001)
assert test_piston.position.y == 0.12
assert test_piston.velocity == 0
assert test_piston.last_position.y == 0.12
print(test_piston.position.y, test_piston.velocity, test_piston.last_position.y)
print("Unit Test Passed")

# Test update with normal y change
test_piston = Piston(1.5, 0.045, 0.05, 0.001, 0.12)
assert test_piston.last_position.y == 0.12
print(test_piston.last_position.y)
test_piston.update(0.11, 0.001)
assert test_piston.position.y == 0.11
assert test_piston.last_position.y == 0.11
print(test_piston.last_position.y)
assert math.isclose(test_piston.velocity, -10, abs_tol=1e-15)
print(test_piston.position.y, test_piston.velocity)
print("Unit Test Passed")