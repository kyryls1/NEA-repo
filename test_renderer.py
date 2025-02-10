import pyglet
import matplotlib.pyplot as plt
from renderer import Renderer
from vector import Vector

def setup_test():
    print("-" * 50)
    flag.update({'called': False})

# Test Cases
def test_valid_data():
    setup_test()
    print("Testing run_plot with valid data...")
    
    time_points = [0, 1, 2, 3]
    torque_points = [10, 15, 20, 25]
    rpm_points = [1000, 1500, 2000, 2500]
    paused_points = [1.5, 2.5]
    throttle_changes = [(0.5, 0.7), (2.5, 0.9)]
    engine_load_changes = [(1.0, 120), (3.0, 180)]
    parameters = ["Test Plot", 10, 20, 30, 40, 50, 60, 70, 80]

    Renderer.run_plot(time_points, torque_points, rpm_points, paused_points, 
                     throttle_changes, engine_load_changes, parameters)
    
    print(f"Plot function called: {flag['called']}")
    assert flag['called'] is True
    print("✓ Unit Test passed: Valid data plotted successfully")

def test_empty_data():
    setup_test()
    print("Testing run_plot with empty data...")
    
    Renderer.run_plot([], [], [], [], [], [], ["Test Plot", 10, 20, 30, 40, 50, 60, 70, 80])
    
    print(f"Plot was called: {flag['called']} (expected: False)")
    assert flag['called'] is False
    print("✓ Unit Test passed: Empty data handled correctly")

def test_mismatched_lengths():
    setup_test()
    print("Testing run_plot with mismatched array lengths...")
    
    time_points = [0, 1, 2]
    torque_points = [10, 15]
    rpm_points = [1000, 1500, 2000]
    parameters = ["Test Plot", 10, 20, 30, 40, 50, 60, 70, 80]
    
    print(f"Array lengths - times: {len(time_points)}, torques: {len(torque_points)}, rpms: {len(rpm_points)}")
    
    Renderer.run_plot(time_points, torque_points, rpm_points, [], [], [], parameters)
    
    print(f"Plot was called: {flag['called']} (expected: False)")
    assert flag['called'] is False
    print("✓ Unit Test passed: Mismatched lengths handled correctly")

def test_invalid_parameters():
    setup_test()
    print("Testing run_plot with invalid parameters format...")
    
    time_points = [0, 1, 2]
    torque_points = [10, 15, 20]
    rpm_points = [1000, 1500, 2000]
    invalid_parameters = "Not a list"
    
    print(f"Testing with invalid parameters type: {type(invalid_parameters)}")
    
    Renderer.run_plot(time_points, torque_points, rpm_points, [], [], [], invalid_parameters)
    print(f"Plot was called: {flag['called']} (expected: False)")
    assert flag['called'] is False
    print("✓ Unit Test passed: Invalid parameters handled correctly")

def test_plot_error():
    setup_test()
    print("Testing run_plot with unexpected plotting error...")
    
    time_points = [0, 1, 2]
    torque_points = [10, 15, 20]
    rpm_points = [1000, 1500, 2000]
    parameters = ["Test Plot", 10, 20, 30, 40, 50, 60, 70, 80]
    
    # Mock matplotlib to force an error during plotting
    def mock_plot(*args, **kwargs):
        raise ValueError("Mock plotting error")
    
    plt.figure = mock_plot

    Renderer.run_plot(time_points, torque_points, rpm_points, [], [], [], parameters)
    print(f"Plot was called: {flag['called']} (expected: False)")
    assert flag['called'] is False
    print("✓ Unit Test passed: Plotting error handled gracefully")

# Run Tests
if __name__ == "__main__":
    # Test Setup
    batch = pyglet.graphics.Batch()
    origin = Vector(0, 0)
    renderer = Renderer(batch, origin, 0.05, 0.1, 0.02, 0.04)

    # Mock matplotlib to track plot calls
    flag = {'called': False}
    plt.show = lambda: flag.update({'called': True})

    print("Running renderer.py tests...")
    test_valid_data()
    test_empty_data()
    test_mismatched_lengths()
    test_invalid_parameters()
    test_plot_error()
    print("-" * 50)
    print("All tests completed.")