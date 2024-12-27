import pyglet
from pyglet import shapes
from pyglet.window import key

class Object():
    def __init__(self, x, y, v):
        self.object = shapes.Rectangle(x=x, y=y, width=100, height=100, color=(50, 225, 30))
        self.position_x = x+50
        self.position_y = y+50
        self.velocity = v
        self.mass = 1
        self.stuck_together = False

    def update(self, dt):
        self.position_x += self.velocity * dt
        self.object.x = self.position_x - 50
    
    def is_colliding(self, other_object):
        if self == other_object:
            return False
        else:
            distance = abs(self.position_x - other_object.position_x)
            overlap_distance = (self.object.width / 2) + (other_object.object.width / 2)
            if distance <= overlap_distance and not self.stuck_together:
                return True
            else:
                return False

class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)

        self.objects = [Object(400, 200, 0), Object(200, 200, 50)]

    def on_draw(self):
        self.clear()
        for i in self.objects:
            i.object.draw()

    def update(self, dt):
        for i in self.objects:
            i.update(dt)
            for j in self.objects:
                if i.is_colliding(j):
                    self.momentum_update(i, j)

    def momentum_update(self, object1, object2):
        velocity_final = ((object1.mass * object1.velocity) + (object2.mass * object2.velocity)) / (object1.mass + object2.mass)
        print(velocity_final)
        object1.velocity = velocity_final
        object2.velocity = velocity_final
        object1.stuck_together = True
        object2.stuck_together = True

if __name__ == "__main__":
    simulation = GameWindow(width=1280, height=720, caption="Simulation", resizable = True)
    pyglet.clock.schedule_interval(simulation.update, 1/30)
    pyglet.app.run()