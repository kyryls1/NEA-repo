import math
import numpy as np
import matplotlib.pyplot as plt
from vector import Vector
from simulation import GasSimulation
from mechanicalComponents import Crank, ConnectorRod, Piston

class GasSimulation():
    def __init__(self, crank_radius, connector_rod_length, deck_clearance):
        self.combustion_temperature = 2273
        self.ambient_temperature = 623
        self.moles_after_combustion = 9/76 * 5
        self.moles_before_combustion = 17/114 * 5
        self.temperature_difference = self.combustion_temperature - self.ambient_temperature
        self.moles_difference = self.moles_after_combustion - self.moles_before_combustion
        self.cylinder_head_position = Vector(0, crank_radius + connector_rod_length + deck_clearance)

    def update_fuel_flow_rate(self, mass_flow_rate):
        self.moles_before_combustion = mass_flow_rate * 9/76
        self.moles_after_combustion = mass_flow_rate * 17/114
        print(self.moles_before_combustion)
        print(self.moles_after_combustion)

    def get_temperature(self, theta):
        if 0 <= theta < 0.1:
            return self.combustion_temperature
        elif 0.1 <= theta <= math.pi:
            return self.ambient_temperature + (self.temperature_difference) * math.exp(-1.5 * (theta - 0.1))
        else:
            multiplier = (theta - math.pi) / math.pi
            increase_amplitude = 0.1 * (self.temperature_difference)
            return self.ambient_temperature + increase_amplitude * (1 - math.cos(math.pi * multiplier))

    def get_gas_moles(self, theta):

        if 0 <= theta < 2:
            return self.moles_after_combustion
        elif 2 <= theta <= 5.2:
            return self.moles_before_combustion + (self.moles_difference) * math.exp(-2.2 * (theta - 2))
        else:
            multiplier = (theta - 5.2) / (2*math.pi - 5.2)
            increase_amplitude = 0.03 * (self.moles_difference)
            return self.moles_before_combustion + increase_amplitude * math.sin(multiplier * math.pi/2)
        
        #return self.moles_before_combustion + (self.moles_after_combustion - self.moles_before_combustion) * (1 + math.sin(theta)) / 2

    def get_current_deck_clearance(self, piston_position):
        return self.cylinder_head_position.y - piston_position.y
        
    def calculate_force(self, theta, piston_position):
        temperature = self.get_temperature(theta)
        mols = self.get_gas_moles(theta)
        gas_volume_height = self.get_current_deck_clearance(piston_position)
        pressure = mols*8.31*temperature
        force = pressure/gas_volume_height
        return force

def test_gas_force():
    # Initialize simulation with same parameters
    crank_radius = 0.05      # 50 mm
    rod_length = 0.15        # 150 mm
    deck_clearance = 0.02    # 20 mm

    sim = GasSimulation(crank_radius, rod_length, deck_clearance)
    crank = Crank(crank_radius, 0)
    rod = ConnectorRod(0, rod_length, crank_radius)
    piston = Piston(0, 0.02, 0.06, deck_clearance, rod_offset=rod.rod_start.y)

    # Generate two complete cycles
    num_points = 2000
    thetas = np.linspace(0, 4 * math.pi, num_points)
    
    last_angle = 0.0
    dt = 1.0 / num_points
    forces = []
    clearances = []
    
    for angle in thetas:
        delta_theta = angle - last_angle
        last_angle = angle

        crank.update_angle(delta_theta)
        rod.update(delta_theta)
        piston.update(rod.rod_end.y, dt)

        # Calculate force and make it negative after π in each cycle
        force = sim.calculate_force(angle % (2 * math.pi), piston.position)
        if (angle % (2 * math.pi)) > math.pi:
            force = -force
            
        clearance = sim.get_current_deck_clearance(piston.position)
        forces.append(force)
        clearances.append(clearance)

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(np.degrees(thetas), forces, color='red', label='Gas Force')
    ax1.set_xlabel('Crank Angle (Degrees)')
    ax1.set_ylabel('Force (N)')
    ax1.set_title('Gas Force Over Two Cycles (Real Sim Logic)')
    ax1.grid(True)
    ax1.legend()

    # Plot deck clearance
    ax2.plot(np.degrees(thetas), clearances, color='blue', label='Deck Clearance')
    ax2.set_xlabel('Crank Angle (Degrees)')
    ax2.set_ylabel('Clearance (m)')
    ax2.set_title('Deck Clearance Over Two Cycles')
    ax2.grid(True)
    ax2.legend()

    # Add vertical lines for both cycles
    for ax in [ax1, ax2]:
        for angle in [0, 180, 360, 540, 720]:
            ax.axvline(x=angle, color='gray', linestyle='--', alpha=0.5)
            if angle in [0, 360, 720]:
                ax.text(angle, ax.get_ylim()[1], 'TDC', rotation=90)
            elif angle in [180, 540]:
                ax.text(angle, ax.get_ylim()[1], 'BDC', rotation=90)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    test_gas_force()