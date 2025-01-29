import math
import matplotlib.pyplot as plt
from linked_list import LinkedList
from vector import Vector

class Crank():
    def __init__(self, radius, mass): 
        self.RADIUS = radius
        self.MASS = mass
        self.MOMENT_OF_INERTIA = self.MASS * self.RADIUS**2
        self.engine_load = 0
        self.starter_motor_torque = 20
        self.starter_motor_on = False
        self.torque_history = LinkedList()

        self.angular_velocity = 0
        self.angle_radians = 0
        self.instantenous_torque = 0
        self.total_torque = 0
 
    def update_engine_load(self, load):
        self.engine_load = load
        
    def calculate_torque(self, force):
        return force * (self.RADIUS)

    def calculate_delta_theta(self, dt):
        return self.angular_velocity * dt

    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)

    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INERTIA
        self.angular_velocity += angular_velocity_change

    def subtract_engine_load(self, torque, crank_angle):
        if self.angular_velocity == 0:
            return torque
        
        load_torque = self.engine_load / -self.angular_velocity
        return torque + load_torque

    def update(self, force, dt):
        self.instantenous_torque = self.calculate_torque(force)
        self.total_torque = self.subtract_engine_load(self.instantenous_torque, self.angle_radians)
        if self.starter_motor_on:
            self.total_torque += self.starter_motor_torque

        self.update_angular_velocity(self.total_torque, dt)
        self.update_angle(self.calculate_delta_theta(dt))

    def get_rpm(self):
        print(self.angular_velocity * 60 / (2 * math.pi))
        return self.angular_velocity * 60 / (2 * math.pi)

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

        self.rod_start.x += delta_x
        self.rod_start.y += delta_y
 
    def update_piston_anchor_position(self):
        delta_x = self.rod_end.x - self.rod_start.x
        new_y = math.sqrt(self.LENGTH_SQUARED - delta_x ** 2) + self.rod_start.y
        self.rod_end.y = new_y

    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston():
    def __init__(self, mass, radius, length, deck_clearance, rod_offset,):
        self.RADIUS = radius
        self.MASS = mass
        self.LENGTH = length
        self.DECK_CLEARANCE = deck_clearance
        self.position = Vector(0, rod_offset)
        self.last_position = Vector(0, rod_offset)

        self.velocity = 0
        self.previous_velocity = 0
        self.surface_area = 2 * math.pi * self.RADIUS * self.LENGTH

    def update_velocity(self, dt):
        dy = (self.position.y - self.last_position.y)
        self.velocity = dy / dt
        self.last_position.y = self.position.y
        self.previous_velocity = self.velocity

    def update(self, y_coordinate, dt):
        self.position.y = y_coordinate
        self.update_velocity(dt)
