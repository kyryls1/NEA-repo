import pyglet
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread

class Vector():
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
        return math.sqrt(abs(self.x**2 + self.y**2))
 
class Crank():
    def __init__(self, radius, mass, batch):
        self.crankarm = pyglet.shapes.Line(x=400, y=400, x2=400, y2=520, width=40, color=[255, 255, 255], batch=batch)
        self.bearing = pyglet.shapes.Circle(x=400, y=400, radius=20, color=[255, 255, 255], batch=batch)
 
        self.RADIUS = radius
        self.MASS = mass
        self.MOMENT_OF_INTERTIA = self.MASS * self.RADIUS**2
 
        self.angular_velocity = 0
        self.angle_radians = 0
 
    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        if self.angle_radians >= 2 * math.pi:
            self.angle_radians -= 2 * math.pi

        angle_degrees = math.degrees(self.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.bearing.rotation = angle_degrees
 
    def get_delta_theta(self, dt):
        return self.angular_velocity * dt
   
    def get_torque(self, force):
        return force * self.RADIUS
 
    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INTERTIA
        self.angular_velocity += angular_velocity_change
 
    def update(self, force, dt):
        torque = self.get_torque(force)
        self.update_angular_velocity(torque, dt)
        self.update_angle(self.get_delta_theta(dt))
        return torque
 
class ConnectorRod():
    def __init__(self, mass, batch):
        self.crank_anchor_vector = Vector(0, 100)
        self.rod = pyglet.shapes.Line(x=400, y=500, x2=400, y2=700, width=15, color=[201, 201, 201], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=400, y=500, radius=15, color=[201, 201, 201], batch=batch)
        self.rod_bearing = pyglet.shapes.Circle(x=400, y=700, radius=15, color=[201, 201, 201], batch=batch)
       
        self.MASS = mass
        self.LENGTH = 200
 
    def update_crank_anchor_position(self, delta_theta):
        initial_x = self.crank_anchor_vector.x
        initial_y = self.crank_anchor_vector.y
        self.crank_anchor_vector.rotate(-delta_theta)
        delta_x = self.crank_anchor_vector.x - initial_x
        delta_y = self.crank_anchor_vector.y - initial_y
        self.rod.x += delta_x
        self.rod.y += delta_y
        self.crank_bearing.x += delta_x
        self.crank_bearing.y += delta_y
 
    def update_piston_anchor_position(self):
        delta_x = self.rod.x2 - self.rod.x
        self.rod.y2 = math.sqrt(self.LENGTH**2 - delta_x**2) + self.rod.y
        self.rod_bearing.y = self.rod.y2
   
    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston():
    def __init__(self, radius, mass, batch):
        self.RADIUS = radius * 100
        self.MASS = mass
        self.piston = pyglet.shapes.Rectangle(x=400-self.RADIUS, y=700, width=self.RADIUS*2, height=150, color=[255, 255, 255], batch=batch)

    def update(self, y_coordinate):
        self.piston.y = y_coordinate

class Simulation():
    def __init__(self, radius, crank_mass, rod_mass, piston_mass, piston_radius):
        self.batch = pyglet.graphics.Batch()
        self.crank = Crank(radius, crank_mass, self.batch)
        self.rod = ConnectorRod(rod_mass, self.batch)
        self.piston = Piston(piston_mass,  piston_radius, self.batch)
        self.time_elapsed = 0
 
    def draw(self):
        self.batch.draw()
 
    def update_all(self, dt):
        global force, time_data, torque_data
        torque = self.crank.update(force, dt)
        self.rod.update(self.crank.get_delta_theta(dt))
        self.piston.update(self.rod.rod.y2)
        self.time_elapsed += dt

        # Update graph data
        time_data.append(self.time_elapsed)
        torque_data.append(torque)

        # Limit buffer size for efficiency
        if len(time_data) > 500:
            time_data.pop(0)
            torque_data.pop(0)

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)
        self.simulation = Simulation(1, 1, 1, 1, 1)
 
    def on_draw(self):
        self.clear()
        self.simulation.draw()
 
    def update(self, dt):
        self.simulation.update_all(dt)
 
    def on_key_press(self, symbol, modifier):
        global force
        if symbol == pyglet.window.key.B:
            force = -2

# Initialize graph data
time_data = []
torque_data = []

# Plotting function for the live graph
def update_graph(frame):
    plt.cla()
    plt.plot(time_data, torque_data, label="Torque vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Torque (Nm)")
    plt.title("Live Torque vs Time Graph")
    plt.legend()

# Start the simulation in a separate thread
def run_simulation():
    global force
    force = 0.1
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable=True)
    pyglet.clock.schedule_interval(simulation.update, 1/60)
    pyglet.app.run()

# Start the graph in the main thread
if __name__ == "__main__":
    simulation_thread = Thread(target=run_simulation)
    simulation_thread.daemon = True
    simulation_thread.start()

    fig = plt.figure()
    ani = FuncAnimation(fig, update_graph, interval=100)
    plt.show()
