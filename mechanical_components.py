import math
from vector import Vector

PI = math.pi
TWO_PI = 2 * PI

class Crank:
    STARTER_MOTOR_TORQUE = 20

    def __init__(self, radius, mass):
        self.radius = radius
        self.mass = mass
        self.moment_of_inertia = 0.5 * self.mass * self.radius**2
        self.engine_load = 0
        self.starter_motor_on = False
        self.angular_velocity = 0
        self.angle_radians = 0
        self.current_torque = 0

    def update_engine_load(self, load):
        self.engine_load = load

    def calculate_torque(self, force):
        return force * (self.radius)

    def calculate_delta_theta(self, dt):
        return self.angular_velocity * dt

    def update_angle(self, delta_theta):
        self.angle_radians = (self.angle_radians + delta_theta) % TWO_PI

    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.moment_of_inertia
        self.angular_velocity += angular_velocity_change

    def subtract_engine_load(self, torque):
        if self.angular_velocity == 0:
            return torque

        load_torque = self.engine_load / -self.angular_velocity
        return torque + load_torque

    def update(self, force, dt):
        input_torque = self.calculate_torque(force)
        self.current_torque = self.subtract_engine_load(input_torque)
        if self.starter_motor_on:
            self.current_torque += self.STARTER_MOTOR_TORQUE

        self.update_angular_velocity(self.current_torque, dt)
        self.update_angle(self.calculate_delta_theta(dt))

    def get_rpm(self):
        return self.angular_velocity * 60 / TWO_PI

class ConnectingRod:
    def __init__(self, mass, length, crank_radius_offset):
        self.mass = mass
        self.length_squared = length**2
        self.crank_anchor = Vector(0, crank_radius_offset)
        self.piston_anchor = Vector(0, length + crank_radius_offset)

    def update_crank_anchor_position(self, delta_theta):
        self.crank_anchor.rotate(-delta_theta)

    def update_piston_anchor_position(self):
        delta_x = self.piston_anchor.x - self.crank_anchor.x
        new_y = math.sqrt(self.length_squared - delta_x ** 2) + self.crank_anchor.y
        self.piston_anchor.y = new_y

    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston:
    def __init__(self, mass, radius, length, deck_clearance, rod_offset):
        self.radius = radius
        self.mass = mass
        self.length = length
        self.deck_clearance = deck_clearance
        self.surface_area = 2 * math.pi * self.radius * self.length
        self.position = Vector(0, rod_offset)
        self.last_position = Vector(0, rod_offset)
        self.velocity = 0

    def update_velocity(self, dt):
        dy = (self.position.y - self.last_position.y)
        self.velocity = dy / dt
        self.last_position.y = self.position.y

    def update(self, y_coordinate, dt):
        self.position.y = y_coordinate
        self.update_velocity(dt)
