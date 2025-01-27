import math
import numpy as np
import matplotlib.pyplot as plt

class GasSimulation():
    def __init__(self):
        self.combustion_temperature = 2273
        self.ambient_temperature = 623
        self.temperature_difference = self.combustion_temperature - self.ambient_temperature
        self.t_min_min = 0.594 * 0.8    # in Kelvin
        self.mol_max = 0.748
        self.mol_min = 0.594
        self.vol_max = 0.5
        self.vol_min = 1

    def get_temperature(self, theta):
        if 0 <= theta < 0.1:
            return self.combustion_temperature
        elif 0.1 <= theta <= math.pi:
            return self.ambient_temperature + (self.temperature_difference) * math.exp(-1.5 * (theta - 0.1))
        else:
            multiplier = (theta - math.pi) / math.pi
            increase_amplitude = 0.1 * (self.temperature_difference)
            return self.ambient_temperature + increase_amplitude * (1 - math.cos(math.pi * multiplier))

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
    temperatures = [sim.get_temperature(theta) for theta in thetas]  # Changed to get temperature
    thetas_deg = np.degrees(thetas)

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(thetas_deg, temperatures, label='Gas Temperature', color='red')  # Changed label and color
    
    # Add stroke transition lines
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=90, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=180, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=270, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=360, color='gray', linestyle='--', alpha=0.5)

    # Add stroke labels with adjusted y-position
    plt.text(45, sim.combustion_temperature, 'Intake', horizontalalignment='center')
    plt.text(135, sim.combustion_temperature, 'Compression', horizontalalignment='center')
    plt.text(225, sim.combustion_temperature, 'Power', horizontalalignment='center')
    plt.text(315, sim.combustion_temperature, 'Exhaust', horizontalalignment='center')

    plt.xlabel('Crank Angle (Degrees)')
    plt.ylabel('Temperature (K)')  # Changed y-axis label
    plt.title('Gas Temperature Variation Over Engine Cycle')  # Changed title
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 360)
    plt.ylim(sim.ambient_temperature - 100, sim.combustion_temperature + 100)  # Adjusted y-axis limits
    plt.show()

if __name__ == "__main__":
    main()