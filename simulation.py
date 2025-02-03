import math
import mechanical_components
from vector import Vector

class GasSimulation():
    STARTING_RPM = 300
    COMBUSTION_TEMPERATURE = 2273
    AMBIENT_TEMPERATURE = 623

    def __init__(self, crank_radius, connector_rod_length, deck_clearance):
        self.moles_after_combustion = 0
        self.moles_before_combustion = 0
        self.temperature_difference = self.COMBUSTION_TEMPERATURE - self.AMBIENT_TEMPERATURE
        self.moles_difference = self.moles_after_combustion - self.moles_before_combustion
        self.deck_surface_position = Vector(0, crank_radius + connector_rod_length + deck_clearance)
        self.decompression_valve_open = True

    def update_fuel_flow_rate(self, mass_flow_rate):
        self.moles_before_combustion = mass_flow_rate * 9/76
        self.moles_after_combustion = mass_flow_rate * 17/114

    def get_temperature(self, theta):
        if 0 <= theta < 0.1:
            return self.COMBUSTION_TEMPERATURE
        elif 0.1 <= theta <= math.pi:
            return self.AMBIENT_TEMPERATURE + (self.temperature_difference) * math.exp(-1.5 * (theta - 0.1))
        else:
            multiplier = (theta - math.pi) / math.pi
            increase_amplitude = 0.1 * (self.temperature_difference)
            return self.AMBIENT_TEMPERATURE + increase_amplitude * (1 - math.cos(math.pi * multiplier))

    def get_gas_moles(self, theta):
        if 0 <= theta < 2:
            return self.moles_after_combustion
        elif 2 <= theta <= 5.2:
            return self.moles_before_combustion + (self.moles_difference) * math.exp(-2.2 * (theta - 2))
        else:
            multiplier = (theta - 5.2) / (2*math.pi - 5.2)
            increase_amplitude = 0.03 * (self.moles_difference)
            return self.moles_before_combustion + increase_amplitude * math.sin(multiplier * math.pi/2)

    def get_current_deck_clearance(self, piston_position):
        return self.deck_surface_position.y - piston_position.y
    
    def calculate_force(self, theta, piston_position):
        temperature = self.get_temperature(theta)
        mols = self.get_gas_moles(theta)
        gas_volume_height = self.get_current_deck_clearance(piston_position)
        
        if self.decompression_valve_open:
            pressure = (mols * 8.31 * temperature) * 0.1
        else:
            pressure = mols * 8.31 * temperature
            
        force = pressure/gas_volume_height
        return force

class Simulation():
    FILM_THICKNESS = 3e-6 
    DYNAMIC_VISCOSITY = 0.01
    PISTON_RING_GRADIENT_COEFFICIENT = -2.5
    PISTON_SKIRT_GRADIENT_COEFFICIENT = -2.1

    def __init__(self, crank_radius, crank_mass, connector_rod_length, rod_mass, piston_radius, piston_mass, piston_length, deck_clearance): 
        self.crank = mechanical_components.Crank(crank_radius, crank_mass)
        self.piston = mechanical_components.Piston(piston_mass,  piston_radius, piston_length, deck_clearance, crank_radius + connector_rod_length)
        self.connector_rod = mechanical_components.ConnectorRod(rod_mass, connector_rod_length, crank_radius)
        self.gas_simulation = GasSimulation(crank_radius, connector_rod_length, deck_clearance)
        self.piston_ring_area = 2 * (2 * math.pi * self.piston.radius * 0.002)
        self.piston_skirt_area = self.piston.surface_area - self.piston_ring_area
        self.component_weight = (rod_mass + piston_mass) * 9.81

    def toggle_starter_motor(self):
        self.crank.starter_motor_on = not self.crank.starter_motor_on
 
    def update_fuel_flow_rate(self, mass_flow_rate):
        self.gas_simulation.update_fuel_flow_rate(mass_flow_rate)

    def update_engine_load(self, engine_load):
        self.crank.update_engine_load(engine_load)
        
    def update_all(self, dt):
        gas_force = self.gas_simulation.calculate_force(self.crank.angle_radians, self.piston.position)
        friction_force = self.calculate_friction()
        total_force = gas_force + self.component_weight - friction_force
        rod_direction_vector = self.find_rod_direction_vector()
        force_parallel_to_rod = self.transfer_force_to_rod(total_force, rod_direction_vector)
        force_tangent_to_crank = self.transfer_force_to_crank(force_parallel_to_rod, rod_direction_vector)

        self.crank.update(force_tangent_to_crank, dt)
        self.connector_rod.update(self.crank.calculate_delta_theta(dt))
        self.piston.update(self.connector_rod.rod_end.y, dt)

    def calculate_velocity_gradient(self, velocity, film_thickness, gradient_coefficient):
        return gradient_coefficient * velocity / film_thickness**2

    def calculate_pressure_gradient(self, dynamic_viscosity, film_thickness, gradient_coefficient):
        velocity_gradient = self.calculate_velocity_gradient(self.piston.velocity, film_thickness, gradient_coefficient)
        return dynamic_viscosity * velocity_gradient

    def calculate_friction(self):
        ring_pressure_gradient = self.calculate_pressure_gradient(self.DYNAMIC_VISCOSITY, self.FILM_THICKNESS, self.PISTON_RING_GRADIENT_COEFFICIENT)
        ring_shear_stress = 0.5 * self.FILM_THICKNESS * ring_pressure_gradient + self.DYNAMIC_VISCOSITY * self.piston.velocity / self.FILM_THICKNESS
        ring_friction = ring_shear_stress * self.piston_ring_area
        skirt_pressure_gradient = self.calculate_pressure_gradient(self.DYNAMIC_VISCOSITY, self.FILM_THICKNESS, self.PISTON_SKIRT_GRADIENT_COEFFICIENT)
        skirt_shear_stress = 0.5 * self.FILM_THICKNESS * skirt_pressure_gradient + self.DYNAMIC_VISCOSITY * self.piston.velocity / self.FILM_THICKNESS
        skirt_friction = skirt_shear_stress * self.piston_skirt_area

        return ring_friction + skirt_friction

    def find_normal_to_crank_motion(self, theta):
        if theta == math.pi/2:
            return Vector(0, 1)
        else:
            return Vector(1, math.tan(theta))
   
    def find_rod_direction_vector(self):
        return Vector(self.connector_rod.rod_end.x - self.connector_rod.rod_start.x, self.connector_rod.rod_end.y - self.connector_rod.rod_start.y)
    
    def transfer_force_to_rod(self, force, rod_direction_vector):
        piston_to_rod_angle = rod_direction_vector.angle_between(Vector(0, 1))

        return force/math.cos(piston_to_rod_angle)
 
    def transfer_force_to_crank(self, force, rod_direction_vector):
        normalised_angle = (-self.crank.angle_radians + math.pi/2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)

        if self.crank.angle_radians < math.pi:
            return -math.cos(rod_to_crank_angle) * force
        else:
            return math.cos(rod_to_crank_angle) * force
