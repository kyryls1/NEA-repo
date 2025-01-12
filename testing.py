import matplotlib.pyplot as plt
import numpy as np
import main

sim = main.GasSimulation()
thetas = np.linspace(0, 2 * np.pi, 1000)
temperatures = [sim.get_temperature(theta) for theta in thetas]

plt.plot(thetas, temperatures)
plt.xlabel("Crank Angle (radians)")
plt.ylabel("Temperature (K)")
plt.title("Temperature vs Crank Angle in 2-Stroke Engine")
plt.show()