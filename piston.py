import pyglet

class Piston():
    def __init__(self, mass, radius, batch):
        self.RADIUS = radius * 100 #CHANGE THIS TO BE TO SCALE LATER!!
        self.MASS = mass

        self.piston = pyglet.shapes.Rectangle(x=400-self.RADIUS, y=700, width=self.RADIUS*2, height=150, color=[255, 255, 255], batch=batch)

    def update(self, y_coordinate):
        self.piston.y = y_coordinate
