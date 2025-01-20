import math
import numpy as np
import matplotlib.pyplot as plt

class GasSimulation:
    def __init__(self):
        self.t_max = 2273  # Maximum temperature at ignition (in Kelvin)
        self.t_min = 623   # Minimum temperature after expansion (in Kelvin)
        self.mol_max = 0.748
        self.mol_min = 0.594
        self.vol_max = 0.5
        self.vol_min = 1
        self.t_difference = self.t_max - self.t_min

    def get_temperature(self, theta):
        theta_mod = theta % (2 * math.pi)

        # 1) Near ignition (theta ~ 0 rad), temperature is briefly at max:
        if 0 <= theta_mod < 0.1:
            return self.t_max

        # 2) From theta=0.1 to theta=pi, exponentially decay from max to min:
        elif 0.1 <= theta_mod <= math.pi:
            k = 2  # Decay rate calculated for ~99% decay by theta=pi
            return self.t_min + (self.t_max - self.t_min) * math.exp(-k * (theta_mod - 0.1))

        # 3) From theta=pi to theta=2pi, stay near min but allow a small “compression” bump:
        else:
            fraction = (theta_mod - math.pi) / math.pi  # Goes 0→1 as theta goes pi→2pi
            amplitude = 0.1 * (self.t_max - self.t_min)  # 10% bump
            # Rises to ~20% bump at 2pi because: 1 - cos(pi*1) = 2
            return self.t_min + amplitude * (1 - math.cos(math.pi * fraction))

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