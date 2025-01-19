import pyglet
from vector import Vector
import math

class Renderer:
    def __init__(self, batch, origin, crank_radius, rod_length, piston_radius):
        self.batch = batch
        self.origin = origin
        self.crank_radius = crank_radius
        self.rod_length = rod_length
        self.piston_radius = piston_radius

        self.axle = pyglet.shapes.Circle(x=origin.x, y=origin.y, radius=20, color=[201, 201, 201], batch=batch)
        self.crankarm = pyglet.shapes.Line(x=origin.x, y=origin.y, x2=origin.x, y2=origin.y + crank_radius, 
                                           thickness=40, color=[255, 255, 255], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius, 
                                                  radius=20, color=[255, 255, 255], batch=batch)        
        self.piston = pyglet.shapes.Rectangle(x=origin.x - piston_radius, y=origin.y + crank_radius + rod_length, 
                                              width=piston_radius * 2, height=150, color=[255, 255, 255], batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius + rod_length, 
                                                   radius=15, color=[201, 201, 201], batch=batch)
        self.rod = pyglet.shapes.Line(x=origin.x, y=origin.y + crank_radius, x2=origin.x, 
                                      y2=origin.y + crank_radius + rod_length, thickness=15, color=[201, 201, 201], batch=batch)
                                                  
    def render(self, crank, rod, piston):
        crank_x = self.origin.x
        crank_y = self.origin.y

        angle_degrees = math.degrees(crank.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.axle.rotation = angle_degrees

        self.rod.x = crank_x + rod.rod_start.x
        self.rod.y = crank_y + rod.rod_start.y
        self.rod.x2 = crank_x + rod.rod_end.x
        self.rod.y2 = crank_y + rod.rod_end.y

        self.crank_bearing.x = self.rod.x
        self.crank_bearing.y = self.rod.y
        self.piston_bearing.x = self.rod.x2
        self.piston_bearing.y = self.rod.y2

        self.piston.x = crank_x - piston.RADIUS
        self.piston.y = crank_y + piston.position.y