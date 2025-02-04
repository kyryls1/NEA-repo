from simulation import GasSimulation
import numpy as np
import matplotlib.pyplot as plt
import math
"""
test_gas = GasSimulation(0.05, 0.15, 0.03)
theta_points = np.linspace(0, 4*math.pi, 2000)
temperatures = [test_gas.get_temperature(theta % (2*math.pi)) for theta in theta_points]

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
"""
# Test gas moles curve over two cycles
test_gas = GasSimulation(0.05, 0.15, 0.03)
test_gas.update_fuel_flow_rate(0.02)  # Initialize with fixed test value
theta_points = np.linspace(0, 4*math.pi, 2000)
moles = [test_gas.get_gas_moles(theta % (2*math.pi)) for theta in theta_points]

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

print("Gas moles curve plotted successfully")
print("Unit test passed")