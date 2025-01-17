import pyglet
import math

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
 
        self.angular_velocity = 5 # fix to start properly later, but have this here so the engine actually starts
        self.angle_radians = 0
 
    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)

        angle_degrees = math.degrees(self.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.bearing.rotation = angle_degrees
 
    def get_delta_theta(self, dt):
        return self.angular_velocity * dt
   
    def get_torque(self, force):
        return force * self.RADIUS / 100
 
    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INTERTIA
        self.angular_velocity += angular_velocity_change

        if self.angular_velocity > 300:
            self.angular_velocity = 300

        #rpm = self.angular_velocity * 60 / (2 * math.pi)
        #print(rpm)
 
    def update(self, force, dt):
        torque = self.get_torque(force)
        print(torque)
        self.update_angular_velocity(torque, dt)
        self.update_angle(self.get_delta_theta(dt))
