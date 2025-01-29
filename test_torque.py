import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 6*np.pi, 100)
y = np.sin(x)

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

for phase in np.linspace(0, 10*np.pi, 500):
    line1.set_ydata(np.sin(x + phase))
    fig.canvas.draw()
    fig.canvas.flush_events()

#piston friction deprecated calculations


    def calculate_viscosity(self, temperature):
        # Simple Arrhenius formula: eta = A * exp(B / T)
        # T assumed to be > 0 K
        if temperature <= 0:
            temperature = 1  # avoid zero or negative

        viscosity = self.visc_A * math.exp(self.visc_B / temperature)
        viscosity = max(1e-6, viscosity)  # Minimum 1e-6 Pa·s

        return viscosity

    def calculate_film_thickness(self, load_force, temperature):
        # Basic EHD approximation: film_thickness ~ c * (eta * velocity / load)^exponent
        # load_force is approximate normal load
        eta = self.calculate_viscosity(temperature)  # fallback for no temperature data, or use last known
        velocity = abs(self.velocity)
        if load_force <= 0:  # avoid negative or zero
            load_force = 1
        
        film_thickness = self.ehd_constant * ((eta * velocity) / load_force) ** self.ehd_exponent
        film_thickness = max(1e-7, film_thickness)  # Minimum 0.1 microns
        film_thickness = min(1e-3, film_thickness)

        return film_thickness
