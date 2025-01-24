import math
import matplotlib.pyplot as plt
import time
from linked_list import LinkedList
from vector import Vector

class Crank():
    def __init__(self, radius, mass): 
        self.RADIUS = radius
        self.MASS = mass
        self.MOMENT_OF_INTERTIA = self.MASS * self.RADIUS**2
        self.torque_history = LinkedList()

        self.angular_velocity = 2 # fix to start properly later, but have this here so the engine actually starts
        self.angle_radians = 0
        self.instantenous_torque = 0
 
    def calculate_torque(self, force):
        return force * (self.RADIUS)

    def calculate_delta_theta(self, dt):
        return self.angular_velocity * dt

    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)

    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INTERTIA
        self.angular_velocity += angular_velocity_change

        #if self.angular_velocity > 40:
           # self.angular_velocity = 40

        rpm = self.angular_velocity * 60 / (2 * math.pi)
        print(rpm)
 
    def update(self, force, dt):
        self.instantenous_torque = self.calculate_torque(force)
        self.update_angular_velocity(self.instantenous_torque, dt)
        self.update_angle(self.calculate_delta_theta(dt))

class ConnectorRod():
    def __init__(self, mass, length, crank_radius_offset):       
        self.MASS = mass
        self.LENGTH_SQUARED = length**2
        self.crank_anchor_vector = Vector(0, crank_radius_offset)
        self.rod_start = Vector(0, crank_radius_offset)
        self.rod_end = Vector(0, length)
 
    def update_crank_anchor_position(self, delta_theta):
        initial_x = self.crank_anchor_vector.x
        initial_y = self.crank_anchor_vector.y

        self.crank_anchor_vector.rotate(-delta_theta) # use negative theta as the matrix rotation is clockwise
        delta_x = self.crank_anchor_vector.x - initial_x
        delta_y = self.crank_anchor_vector.y - initial_y

        #self.rod.x += delta_x
        #self.rod.y += delta_y
        #self.crank_bearing.x += delta_x
        #self.crank_bearing.y += delta_y
        self.rod_start.x += delta_x
        self.rod_start.y += delta_y
 
    def update_piston_anchor_position(self):
        delta_x = self.rod_end.x - self.rod_start.x
        #self.rod.y2 = math.sqrt(self.LENGTH**2 - delta_x**2) + self.rod.y
        #self.piston_bearing.y = self.rod.y2
        delta_x_squared = delta_x ** 2
        if delta_x_squared > self.LENGTH_SQUARED:
            # Clamp delta_x to ensure delta_x^2 <= L^2
            sign = 1 if delta_x >= 0 else -1
            delta_x = sign * self.LENGTH * 0.999  # Slightly less than L to avoid sqrt(0)
            print(f"Warning: delta_x ({delta_x}) clamped to prevent sqrt of negative number.")

        try:
            new_y = math.sqrt(self.LENGTH_SQUARED - delta_x ** 2) + self.rod_start.y
            self.rod_end.y = new_y
        except ValueError:
            # In case of unexpected negative value due to floating-point inaccuracies
            self.rod_end.y = self.rod_start.y + self.LENGTH
            print("Error: sqrt received a negative value. Setting rod_end.y to maximum feasible value.")

    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston():
    def __init__(self, mass, radius, rod_offset):
        self.RADIUS = radius
        self.MASS = mass
        self.position = Vector(0, rod_offset)
        # Store last position to compute velocity via position delta
        self.last_position = Vector(0, rod_offset)

        # Arrhenius-type viscosity constants (approx. for engine oil)
        self.visc_A = 0.015    # Pa·s coefficient
        self.visc_B = 2000     # exponent coefficient

        self.contact_height = 0.1  # m
        self.ambient_pressure = 1e5

        self.ehd_constant = 1e-5
        self.ehd_exponent = 0.7

        self.velocity = 0
        self.previous_velocity = 0

    def update_velocity(self, dt):
        # Piston movement in mm over dt, then convert to m/s
        dy = (self.position.y - self.last_position.y)
        self.velocity = dy / dt
        self.last_position.y = self.position.y
        self.previous_velocity = self.velocity

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

    def calculate_friction(self, temperature, load_force, angular_velocity):
        # Updated friction formula using film thickness & Arrhenius viscosity
        visc = self.calculate_viscosity(temperature)
        film_thickness = self.calculate_film_thickness(load_force, temperature)

        contact_area = 2 * math.pi * self.RADIUS * self.contact_height
        friction_magnitude = visc * (self.velocity / film_thickness) * contact_area

        return math.copysign(friction_magnitude, self.velocity)

    def update(self, y_coordinate, dt):
        self.position.y = y_coordinate
        self.update_velocity(dt)
