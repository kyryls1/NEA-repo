import pyglet
import math
import matplotlib.pyplot as plt
import time
from collections import deque

class Crank():
    def __init__(self, radius, mass, batch):
        # crank = pyglet.image.load('testsprite.png')   add later if I use actual sprite
        # crank.anchor_x = round(crank.width / 2)
        # crank.anchor_y = round(crank.height / 2)
 
        self.crankarm = pyglet.shapes.Line(x=400, y=400, x2=400, y2=520, thickness=40, color=[255, 255, 255], batch=batch)
        self.bearing = pyglet.shapes.Circle(x=400, y=400, radius=20, color=[255, 255, 255], batch=batch)
 
        self.RADIUS = radius
        self.MASS = mass
        self.MOMENT_OF_INTERTIA = self.MASS * self.RADIUS**2
        self.torque_history = deque(maxlen=100000)
        self.start_time = time.perf_counter()

        self.angular_velocity = 5 # fix to start properly later, but have this here so the engine actually starts
        self.angle_radians = 0
 
    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)

        angle_degrees = math.degrees(self.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.bearing.rotation = angle_degrees
 
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
        # Store time and torque
        current_time = time.perf_counter() - self.start_time
        self.torque_history.append((current_time, torque))
        #print(torque)
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