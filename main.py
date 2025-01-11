import pyglet
import math
import crank, connectorRod, piston
from vector import Vector


class GasSimulation():
    def __init__(self):
        self.t_max = 2273
        self.t_min = 623
        
    def get_temperature(self, theta):
        return self.t_max - (self.t_max - self.t_min) * abs(math.cos(theta))
    
    def calculate_force_during_downstroke(self, theta, dt):
        temperature = self.get_temperature(theta)
        cylinder_height = 0.05
        pressure = 0.748*8.31*temperature
        force = pressure/cylinder_height
        print(force)
        return force

    
    def calculate_force_during_upstroke(self, theta, dt):
        temperature = self.get_temperature(theta)
        cylinder_height = 0.05
        pressure = 0.594*8.31*temperature
        force = pressure/cylinder_height
        print(force)
        return force
        
class Simulation():
    def __init__(self, radius, crank_mass, rod_mass, piston_mass, piston_radius):
        self.batch = pyglet.graphics.Batch()
 
        self.crank = crank.Crank(radius, crank_mass, self.batch)
        self.piston = piston.Piston(piston_mass,  piston_radius, self.batch)
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

        rod_direction_vector = self.find_rod_direction_vector()
        force_parallel_to_rod = self.transfer_force_to_rod(force, rod_direction_vector)
        force_tangent_to_crank = self.transfer_force_to_crank(force_parallel_to_rod, rod_direction_vector)

        self.crank.update(force_tangent_to_crank, dt)
        self.rod.update(self.crank.get_delta_theta(dt))
        self.piston.update(self.rod.rod.y2)
 
    def find_normal_to_crank_motion(self, theta):
        if theta == math.pi/2:
            return Vector(0, 1)
        else:
            return Vector(1, math.tan(theta))
   
    def find_rod_direction_vector(self):
        return Vector(self.rod.rod.x2 - self.rod.rod.x, self.rod.rod.y2 - self.rod.rod.y) #this naming convention looks so stupid
    
    def transfer_force_to_rod(self, force, rod_direction_vector):
        piston_to_rod_angle = rod_direction_vector.angle_between(Vector(0, 1))
        total_downward_force = force + self.component_weight

        return math.cos(piston_to_rod_angle) * total_downward_force
 
    def transfer_force_to_crank(self, force, rod_direction_vector):
        normalised_angle = (-self.crank.angle_radians + math.pi/2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)

        if self.crank.angle_radians < math.pi:
            return -math.cos(rod_to_crank_angle) * force
        else:
            return math.cos(rod_to_crank_angle) * force
 
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

if __name__ == "__main__":
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable = True)
    pyglet.clock.schedule_interval(simulation.update, 1/60)
    pyglet.app.run()
