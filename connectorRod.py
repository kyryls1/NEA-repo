import pyglet
from vector import Vector
import math

class ConnectorRod():
    def __init__(self, mass, batch):
        #self.rod = pyglet.shapes.Line(x=400, y=500, x2=400, y2=700, thickness=15, color=[201, 201, 201], batch=batch)
        #self.crank_bearing = pyglet.shapes.Circle(x=400, y=500, radius=15, color=[201, 201, 201], batch=batch)
        #self.piston_bearing = pyglet.shapes.Circle(x=400, y=700, radius=15, color=[201, 201, 201], batch=batch)
       
        self.MASS = mass
        self.LENGTH = 200 #Remember to change this later!!
        self.crank_anchor_vector = Vector(0, 100)
        self.rod_start = Vector(400, 500)
        self.rod_end = Vector(400, 700)
 
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
