import pyglet
import math
import time
import crank, connectorRod, piston
from vector import Vector
from numba import njit

@njit
def compute_temperature(theta, t_max, t_min):
    """Optimized temperature calculation."""
    if 0 <= theta <= math.pi:
        return t_max - (t_max - t_min) * (theta / math.pi)
    else:
        return t_min + (t_max - t_min) * ((theta - math.pi) / math.pi)

@njit
def compute_downstroke_force(theta, t_max, t_min):
    cylinder_height = 0.05
    temp = compute_temperature(theta, t_max, t_min)
    # Gains from 0.748 * 8.31, done inline here
    return (0.748 * 8.31 * temp) / cylinder_height

@njit
def compute_upstroke_force(theta, t_max, t_min):
    cylinder_height = 0.05
    temp = compute_temperature(theta, t_max, t_min)
    return (0.594 * 8.31 * temp) / cylinder_height

@njit
def angle_between(x1, y1, x2, y2):
    dot = x1*x2 + y1*y2
    mod1 = math.sqrt(x1*x1 + y1*y1)
    mod2 = math.sqrt(x2*x2 + y2*y2)
    # Add small epsilon to avoid zero division
    return math.acos(dot / (mod1*mod2 + 1e-12))

@njit
def find_rod_direction(rod_x1, rod_y1, rod_x2, rod_y2):
    return (rod_x2 - rod_x1, rod_y2 - rod_y1)

@njit
def compute_force_parallel_to_rod(force, weight, rod_dx, rod_dy):
    piston_to_rod_angle = angle_between(rod_dx, rod_dy, 0.0, 1.0)
    return math.cos(piston_to_rod_angle) * (force + weight)

@njit
def compute_force_tangent_to_crank(force_parallel, angle_radians, rod_dx, rod_dy):
    normalised_angle = (-angle_radians + math.pi/2) % (2 * math.pi)
    nx, ny = (1.0, math.tan(normalised_angle))
    rod_to_crank_angle = 3*math.pi/2 - angle_between(nx, ny, rod_dx, rod_dy)
    if angle_radians < math.pi:
        return -math.cos(rod_to_crank_angle) * force_parallel
    else:
        return math.cos(rod_to_crank_angle) * force_parallel

class GasSimulation():
    def __init__(self):
        self.t_max = 2273
        self.t_min = 623

    def calculate_force_during_downstroke(self, theta, dt):
        return compute_downstroke_force(theta, self.t_max, self.t_min)

    def calculate_force_during_upstroke(self, theta, dt):
        return compute_upstroke_force(theta, self.t_max, self.t_min)

class Simulation():
    def __init__(self, radius, crank_mass, rod_mass, piston_mass, piston_radius):
        self.batch = pyglet.graphics.Batch()
        self.crank = crank.Crank(radius, crank_mass, self.batch)
        self.piston = piston.Piston(piston_mass, piston_radius, self.batch)
        self.rod = connectorRod.ConnectorRod(rod_mass, self.batch)

        self.component_weight = (rod_mass + piston_mass) * 9.81
        self.gas_simulation = GasSimulation()

    def draw(self):
        self.batch.draw()

    def update_all(self, dt):
        if self.crank.angle_radians > math.pi:
            force = self.gas_simulation.calculate_force_during_upstroke(self.crank.angle_radians, dt) / 130
        else:
            force = self.gas_simulation.calculate_force_during_downstroke(self.crank.angle_radians, dt) / 130

        rod_dx, rod_dy = find_rod_direction(self.rod.rod.x, self.rod.rod.y, self.rod.rod.x2, self.rod.rod.y2)
        force_parallel = compute_force_parallel_to_rod(force, self.component_weight, rod_dx, rod_dy)
        force_tangent = compute_force_tangent_to_crank(force_parallel, self.crank.angle_radians, rod_dx, rod_dy)

        self.crank.update(force_tangent, dt)
        self.rod.update(self.crank.calculate_delta_theta(dt))
        self.piston.update(self.rod.rod.y2)

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)
        self.simulation = Simulation(1, 1, 1, 1, 1)
        self.fps_display = pyglet.window.FPSDisplay(self)

        self.simulation_update_count = 0
        self.last_update_time = time.time()

    def on_draw(self):
        self.clear()
        self.simulation.draw()
        self.fps_display.draw()

    def update_simulation(self, dt):
        self.simulation.update_all(dt)
        self.simulation_update_count += 1
        current_time = time.time()
        if current_time - self.last_update_time >= 1:
            print(f"Simulation updates per second: {self.simulation_update_count}")
            self.simulation_update_count = 0  # Reset counter after printing
            self.last_update_time = current_time


if __name__ == "__main__":
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable=True, vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/2000)
    pyglet.app.run(interval=1/30)