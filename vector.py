import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
   
    def rotate(self, angle):
        new_x = self.x * math.cos(angle) + self.y * -math.sin(angle)
        new_y = self.x * math.sin(angle) + self.y * math.cos(angle)
        self.x, self.y = new_x, new_y
       
    def angle_between(self, vector2):
        dot_product = self.x * vector2.x + self.y * vector2.y
        return math.acos(dot_product / (self.modulus() * vector2.modulus()))
   
    def modulus(self):
        return math.sqrt(self.x**2 + self.y**2)