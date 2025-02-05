from simulation import GasSimulation
import numpy as np
import matplotlib.pyplot as plt
import math

# Test update_fuel_flow_rate with zero input
test_gas = GasSimulation(0.05, 0.15, 0.03)
test_gas.update_fuel_flow_rate(0)
assert test_gas.moles_before_combustion == 0
assert test_gas.moles_after_combustion == 0
assert test_gas.moles_difference == 0
assert test_gas.increase_amplitude == 0
print(test_gas.moles_before_combustion, test_gas.moles_after_combustion, test_gas.moles_difference, test_gas.increase_amplitude)
print("Unit Test Passed")

# Test update_fuel_flow_rate with non-zero input
test_gas = GasSimulation(0.05, 0.15, 0.03)
test_gas.update_fuel_flow_rate(1)
assert test_gas.moles_before_combustion == 27/228.46
assert test_gas.moles_after_combustion == 34/228.46
assert math.isclose(test_gas.moles_difference, 7/228.46, abs_tol=1e-15)
assert math.isclose(test_gas.increase_amplitude, 0.03 * (7/228.46), abs_tol=1e-15)
print(test_gas.moles_before_combustion, test_gas.moles_after_combustion, test_gas.moles_difference, test_gas.increase_amplitude)
print("Unit Test Passed")

"""
test_gas = GasSimulation(0.05, 0.15, 0.03)
theta_points = np.linspace(0, 4*math.pi, 2000)
temperatures = [test_gas.get_temperature(theta % (2*math.pi)) for theta in theta_points]

assert len(temperatures) == len(theta_points)
print(len(temperatures))

plt.figure(figsize=(10, 6))
plt.plot(np.degrees(theta_points), temperatures, color='red')
plt.xlabel('Crank Angle (Degrees)')
plt.ylabel('Temperature (K)')
plt.title('Gas Temperature Over Two Engine Cycles')
plt.grid(True)

key_angles = [0, 180, 360, 540, 720]
for angle in key_angles:
    plt.axvline(x=angle, color='blue', linestyle='--', alpha=0.5)
    y_mid = (plt.ylim()[0] + plt.ylim()[1]) / 2
    if angle in [0, 360, 720]:
        plt.text(angle+5, y_mid, 'TDC', rotation=90, verticalalignment='center')
    else:
        plt.text(angle+5, y_mid, 'BDC', rotation=90, verticalalignment='center')

plt.show()


# Test gas moles curve over two cycles
test_gas = GasSimulation(0.05, 0.15, 0.03)
test_gas.update_fuel_flow_rate(1)
theta_points = np.linspace(0, 4*math.pi, 2000)
moles = [test_gas.get_gas_moles(theta % (2*math.pi)) for theta in theta_points]

assert len(moles) == len(theta_points)
print(len(moles))

plt.figure(figsize=(10, 6))
plt.plot(np.degrees(theta_points), moles, color='red')
plt.xlabel('Crank Angle (Degrees)')
plt.ylabel('Gas Moles')
plt.title('Gas Moles Over Two Engine Cycles')
plt.grid(True)

key_angles = [0, 180, 360, 540, 720]
for angle in key_angles: 
    plt.axvline(x=angle, color='blue', linestyle='--', alpha=0.5)
    y_mid = (plt.ylim()[0] + plt.ylim()[1]) / 2
    if angle in [0, 360, 720]:
        plt.text(angle+5, y_mid, 'TDC', rotation=90, verticalalignment='center')
    else:
        plt.text(angle+5, y_mid, 'BDC', rotation=90, verticalalignment='center')

plt.show()
"""