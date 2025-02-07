import pyglet
import matplotlib.pyplot as plt
from renderer import Renderer
from vector import Vector

# ------------------------- Test store_graph_point -------------------------
batch = pyglet.graphics.Batch()
origin = Vector(0, 0)
renderer = Renderer(batch, origin, 0.05, 0.1, 0.02, 0.04)

renderer.store_graph_point(1.0, 10.0, 1000.0)
stored_point = renderer.graph_points.head.data
print(f"Stored graph point: {stored_point}")
assert renderer.graph_points.head.data == (1.0, 10.0, 1000.0)
print("\n✓ Test store_graph_point: Unit Test Passed")

# ------------------------- Test store_paused_point -------------------------
renderer.store_paused_point(2.0)
stored_pause = renderer.paused_points.head.data
print(f"Stored pause point: {stored_pause}")
assert renderer.paused_points.head.data == 2.0
print("\n✓ Test store_paused_point: Unit Test Passed")

# ------------------------- Test store_throttle_change_point -------------------------
renderer.store_throttle_change_point(3.0, 0.8)
stored_throttle = renderer.throttle_change_points.head.data
print(f"Stored throttle change: {stored_throttle}")
assert renderer.throttle_change_points.head.data == (3.0, 0.8)
print("\n✓ Test store_throttle_change_point: Unit Test Passed")

# ------------------------- Test store_engine_load_change_point -------------------------
renderer.store_engine_load_change_point(4.0, 150)
stored_load = renderer.engine_load_change_points.head.data
print(f"Stored engine load change: {stored_load}")
assert renderer.engine_load_change_points.head.data == (4.0, 150)
print("\n✓ Test store_engine_load_change_point: Unit Test Passed")

# ------------------------- Test run_plot with valid data -------------------------
times = [0, 1, 2, 3]
torques = [10, 15, 20, 25]
rpms = [1000, 1500, 2000, 2500]
paused_points = [1.5, 2.5]
throttle_changes = [(0.5, 0.7), (2.5, 0.9)]
engine_load_changes = [(1.0, 120), (3.0, 180)]
parameters = ["Test Plot", 10, 20, 30, 40, 50, 60, 70, 80]

flag = {'called': False}
original_show = plt.show
plt.show = lambda: flag.update({'called': True})

Renderer.run_plot(times, torques, rpms, paused_points, throttle_changes, engine_load_changes, parameters)
print(f"Plot function called: {flag['called']}")
assert flag['called'] is True
plt.show = original_show
print("\n✓ Test run_plot with valid data: Unit Test Passed")

# ------------------------- Test run_plot error cases -------------------------
# Test empty data
print("\nTesting run_plot with empty data...")
flag = {'called': False}
plt.show = lambda: flag.update({'called': True})

Renderer.run_plot([], [], [], [], [], [], parameters)
print(f"Plot was called: {flag['called']} (expected: False)")
assert flag['called'] is False
print("\n✓ Test run_plot empty data error: Unit Test Passed")

# Test mismatched lengths
print("\nTesting run_plot with mismatched lengths...")
times = [0, 1, 2]
torques = [10, 15]  # One element shorter
rpms = [1000, 1500, 2000]
print(f"Testing with lengths - times: {len(times)}, torques: {len(torques)}, rpms: {len(rpms)}")

flag = {'called': False}
plt.show = lambda: flag.update({'called': True})

Renderer.run_plot(times, torques, rpms, [], [], [], parameters)
print(f"Plot was called: {flag['called']} (expected: False)")
assert flag['called'] is False
print("\n✓ Test run_plot mismatched lengths error: Unit Test Passed")

# Test invalid parameters
print("\nTesting run_plot with invalid parameters...")
invalid_parameters = ["Test Plot", 10]  # Too few parameters
print(f"Testing with invalid parameters length: {len(invalid_parameters)}")

flag = {'called': False}
plt.show = lambda: flag.update({'called': True})

Renderer.run_plot(times, torques, rpms, [], [], [], invalid_parameters)
print(f"Plot was called: {flag['called']} (expected: False)")
assert flag['called'] is False
plt.show = original_show
print("\n✓ Test run_plot invalid parameters error: Unit Test Passed")
