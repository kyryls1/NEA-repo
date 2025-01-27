import math
import numpy as np
import matplotlib.pyplot as plt

class GasSimulation():
    def __init__(self):
        self.combustion_temperature = 2273
        self.ambient_temperature = 623
        self.temperature_difference = self.combustion_temperature - self.ambient_temperature
        self.t_min_min = 0.594 * 0.8    # in Kelvin
        self.moles_after_combustion = 9/76 * 5
        self.moles_before_combustion = 17/114 * 5
        self.moles_difference = self.moles_after_combustion - self.moles_before_combustion
        self.vol_max = 0.5
        self.vol_min = 1

    def get_temperature(self, theta):
        return self.moles_before_combustion + (self.moles_after_combustion - self.moles_before_combustion) * (1 + math.sin(theta)) / 2

    def get_gas_mol(self, theta):
        if 0 <= theta < 2:
            return self.t_max

        elif 2 <= theta <= 5.2:
            return self.t_min + (self.t_max - self.t_min) * math.exp(-2.2 * (theta - 2))
        else:
            # Normalize theta between 5.2 and 2π to a 0-1 range
            fraction = (theta - 5.2) / (2*math.pi - 5.2)
            # Smaller amplitude for more realistic rise during intake
            amplitude = 0.03 * (self.t_max - self.t_min)
            # Use sine instead of (1-cos) for a more gradual rise
            return self.t_min + amplitude * math.sin(fraction * math.pi/2)

    def get_height(self, theta):
        # Placeholder function for cylinder height based on theta
        return self.vol_min + (self.vol_max - self.vol_min) * (math.cos(theta) + 1) / 2

    def calculate_force(self, theta, dt):
        temperature = self.get_temperature(theta)
        mols = self.get_gas_mol(theta)
        pressure = mols * 8.31 * temperature  # PV = nRT => P = nRT/V
        force = pressure * math.pi * (self.get_height(theta))**2  # Assuming cylindrical force distribution
        return force
    
def main():
    sim = GasSimulation()

    # Generate theta values from 0 to 2pi radians
    num_points = 1000
    thetas = np.linspace(0, 2 * math.pi, num_points)
    gas_moles = [sim.get_gas_mol(theta) for theta in thetas]
    thetas_deg = np.degrees(thetas)

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(thetas_deg, gas_moles, label='Gas Moles', color='blue')
    
    # Add stroke transition lines
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=90, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=180, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=270, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=360, color='gray', linestyle='--', alpha=0.5)

    # Add stroke labels with adjusted y-position
    plt.text(45, max(gas_moles), 'Intake', horizontalalignment='center')
    plt.text(135, max(gas_moles), 'Compression', horizontalalignment='center')
    plt.text(225, max(gas_moles), 'Power', horizontalalignment='center')
    plt.text(315, max(gas_moles), 'Exhaust', horizontalalignment='center')

    plt.xlabel('Crank Angle (Degrees)')
    plt.ylabel('Gas Moles')
    plt.title('Gas Moles Variation Over Engine Cycle')
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 360)
    plt.ylim(min(gas_moles) - 0.1, max(gas_moles) + 0.1)
    plt.show()

if __name__ == "__main__":
    main()