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
        self.start_time = time.perf_counter()

        self.angular_velocity = 5 # fix to start properly later, but have this here so the engine actually starts
        self.angle_radians = 0
 
    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)
 
    def calculate_delta_theta(self, dt):
        return self.angular_velocity * dt
   
    def calculate_torque(self, force):
        return force * self.RADIUS
 
    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INTERTIA
        self.angular_velocity += angular_velocity_change

        if self.angular_velocity > 300:
            self.angular_velocity = 300

        #rpm = self.angular_velocity * 60 / (2 * math.pi)
        #print(rpm)
 
    def update(self, force, dt):
        torque = self.calculate_torque(force)
        current_time = time.perf_counter() - self.start_time
        self.torque_history.append((current_time, torque))
        self.update_angular_velocity(torque, dt)
        self.update_angle(self.calculate_delta_theta(dt))

    def plot_torque(self):
        times = [t[0] for t in self.torque_history]
        torques = [t[1] for t in self.torque_history]
        plt.plot(times, torques)
        plt.xlabel('Time (s)')
        plt.ylabel('Torque (N·m)')
        plt.title('Crank Torque')
        plt.show()

class ConnectorRod():
    def __init__(self, mass, length, crank_radius_offset):       
        self.MASS = mass
        self.LENGTH = length
        self.crank_anchor_vector = Vector(0, crank_radius_offset)
        self.rod_start = Vector(0, crank_radius_offset)
        self.rod_end = Vector(0, self.LENGTH)
 
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
        self.rod_end.y = math.sqrt(self.LENGTH**2 - delta_x**2) + self.rod_start.y
   
    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston():
    def __init__(self, mass, radius, origin):
        self.RADIUS = radius #CHANGE THIS TO BE TO SCALE LATER!!
        self.MASS = mass
        self.position = Vector(0, origin)
        #self.piston = pyglet.shapes.Rectangle(x=400-self.RADIUS, y=700, width=self.RADIUS*2, height=150, color=[255, 255, 255], batch=batch)

    def update(self, y_coordinate):
        #self.piston.y = y_coordinate
        self.position.y = y_coordinate
