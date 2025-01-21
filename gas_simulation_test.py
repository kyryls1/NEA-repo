import math
import numpy as np
import matplotlib.pyplot as plt

class GasSimulation():
    def __init__(self):
        self.t_max = 2273    # in Kelvin
        self.t_min = 623     # in Kelvin
        self.mol_max = 0.748
        self.mol_min = 0.594
        self.vol_max = 0.5
        self.vol_min = 1
        self.t_difference = self.t_max - self.t_min

    def get_temperature(self, theta):
        # Assuming a sinusoidal temperature variation
        return self.t_min + (self.t_max - self.t_min) * (math.sin(theta) + 1) / 2

    def get_gas_mol(self, theta):
        # Assuming gas moles vary sinusoidally
        return self.mol_min + (self.mol_max - self.mol_min) * (math.sin(theta) + 1) / 2

    def get_height(self, theta):
        # Placeholder function for cylinder height based on theta
        return self.vol_min + (self.vol_max - self.vol_min) * (math.sin(theta) + 1) / 2

    def calculate_force(self, theta, dt):
        temperature = self.get_temperature(theta)
        mols = self.get_gas_mol(theta)
        pressure = mols * 8.31 * temperature  # PV = nRT => P = nRT/V
        force = pressure * math.pi * (self.get_height(theta))**2  # Assuming cylindrical force distribution
        return force
    
def main():
    # Instantiate the GasSimulation class
    sim = GasSimulation()

    # Generate theta values from 0 to 2pi radians
    num_points = 1000  # Number of points in the simulation
    thetas = np.linspace(0, 2 * math.pi, num_points)
    temperatures = [sim.get_temperature(theta) for theta in thetas]

    # Convert theta to degrees for better readability in the plot
    thetas_deg = np.degrees(thetas)

    # Plot the temperature vs. crank angle
    plt.figure(figsize=(12, 6))
    plt.plot(thetas_deg, temperatures, label='Temperature', color='red')
    plt.xlabel('Crank Angle (Degrees)')
    plt.ylabel('Temperature (K)')
    plt.title('Temperature Variation Over a Full Engine Cycle')
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 360)
    plt.ylim(sim.t_min - 50, sim.t_max + 100)  # Adjust y-axis for better visibility
    plt.show()

if __name__ == "__main__":
    main()