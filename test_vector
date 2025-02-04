from vector import Vector
import math
"""
test_vector = Vector(1, 2)
assert test_vector.x == 1
assert test_vector.y == 2
print(test_vector.x, test_vector.y) 
print("Unit Test Passed")
"""
'''
test_vector = Vector(1, 0)
test_vector.rotate(math.pi/2)
assert math.isclose(test_vector.x, 0, abs_tol=1e-15)
assert math.isclose(test_vector.y, 1, abs_tol=1e-15)
print(test_vector.x, test_vector.y)
print("Unit Test Passed")
'''
# Test rotation by negative angle
test_vector = Vector(1, 0)
test_vector.rotate(-math.pi/2)
assert math.isclose(test_vector.x, 0, abs_tol=1e-15)
assert math.isclose(test_vector.y, -1, abs_tol=1e-15)
print(test_vector.x, test_vector.y)
print("Unit Test Passed")

# Test rotation by 0
test_vector = Vector(1, 2)
test_vector.rotate(0)
assert math.isclose(test_vector.x, 1, abs_tol=1e-15)
assert math.isclose(test_vector.y, 2, abs_tol=1e-15)
print(test_vector.x, test_vector.y)
print("Unit Test Passed")

# Test zero vector modulus
test_vector = Vector(0, 0)
modulus = test_vector.modulus()
assert math.isclose(modulus, 0, abs_tol=1e-15)
print(modulus)
print("Unit Test Passed")

# Test negative vector modulus
test_vector = Vector(-3, -4)
modulus = test_vector.modulus()
assert math.isclose(modulus, 5, abs_tol=1e-15)
print(modulus)
print("Unit Test Passed")

# Test angle between vectors in the same direction (towards intersection)
test_vector1 = Vector(1, 0)
test_vector2 = Vector(3, -3)
angle = test_vector1.angle_between(test_vector2)
assert math.isclose(angle, math.pi/4, abs_tol=1e-15)
print(angle)
print("Unit Test Passed")

# Test angle between vectors in opposite directions (one towards, one away from intersection)
test_vector1 = Vector(1, 0)
test_vector2 = Vector(-3, 3)
angle = test_vector1.angle_between(test_vector2)
assert math.isclose(angle, 3*math.pi/4, abs_tol=1e-15)
print(angle)
print("Unit Test Passed")

try:
    test_vector1 = Vector(1, 0)
    test_vector2 = Vector(0, 0)
    angle = test_vector1.angle_between(test_vector2)
    print("Test should have raised exception")
    assert False
except ZeroDivisionError:
    print("Correctly raised ZeroDivisionError")
    print("Unit Test Passed")