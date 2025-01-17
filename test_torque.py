import math
import numpy as np
import matplotlib.pyplot as plt
from main import GasSimulation  # Ensure main.py is in the same directory
from crank import Crank        # Ensure crank.py is in the same directory

# Define a simple Vector class for necessary vector operations
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def angle_between(self, other):
        """
        Calculate the angle between this vector and another vector in radians.
        """
        dot_product = self.x * other.x + self.y * other.y
        magnitude_self = math.hypot(self.x, self.y)
        magnitude_other = math.hypot(other.x, other.y)
        if magnitude_self == 0 or magnitude_other == 0:
            return 0
        cos_angle = dot_product / (magnitude_self * magnitude_other)
        # Clamp the cosine to the valid range to prevent math domain errors
        cos_angle = max(min(cos_angle, 1), -1)
        return math.acos(cos_angle)

class TestTorqueSimulation:
    def __init__(self, radius, mass):
        """
        Initialize the test simulation with a Crank and GasSimulation instance.
        
        Parameters:
            radius (float): Radius of the crank (meters).
            mass (float): Mass of the crank (kg).
        """
        self.gas_sim = GasSimulation()
        self.crank = Crank(radius=radius, mass=mass, batch=None)  # Ensure Crank's __init__ takes (radius, mass, batch)
        self.component_weight = 9.81  # Assuming rod_mass and piston_mass are set to 1 kg each for simplicity
    
    def find_normal_to_crank_motion(self, theta):
        """
        Mimic the Simulation.find_normal_to_crank_motion method.
        """
        if theta == math.pi / 2:
            return Vector(0, 1)
        else:
            try:
                return Vector(1, math.tan(theta))
            except:
                return Vector(1, 0)  # Fallback to horizontal vector if tan(theta) is undefined
    
    def find_rod_direction_vector(self, theta):
        """
        Approximate the rod direction vector based on the current crank angle.
        
        Parameters:
            theta (float): Current crank angle in radians.
        
        Returns:
            Vector: Direction vector of the rod.
        """
        # Corrected attribute access: use lowercase 'radius'
        x2 = self.crank.RADIUS * math.cos(theta)
        y2 = self.crank.RADIUS * math.sin(theta)
        return Vector(x2, y2)  # Assuming piston is at origin
    
    def transfer_force_to_rod(self, force, rod_direction_vector):
        """
        Mimic the Simulation.transfer_force_to_rod method.
        
        Parameters:
            force (float): Downward force applied.
            rod_direction_vector (Vector): Direction vector of the rod.
        
        Returns:
            float: Force parallel to the rod.
        """
        piston_to_rod_angle = rod_direction_vector.angle_between(Vector(0, 1))  # Vector(0,1) is upward
        total_downward_force = force + self.component_weight
        cos_angle = math.cos(piston_to_rod_angle)
        if cos_angle == 0:
            # Avoid division by zero
            return 0
        return total_downward_force / cos_angle
    
    def transfer_force_to_crank(self, force_parallel_to_rod, rod_direction_vector, theta):
        """
        Mimic the Simulation.transfer_force_to_crank method.
        
        Parameters:
            force_parallel_to_rod (float): Force parallel to the rod.
            rod_direction_vector (Vector): Direction vector of the rod.
            theta (float): Current crank angle in radians.
        
        Returns:
            float: Force tangent to the crank.
        """
        normalised_angle = (-theta + math.pi / 2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)
    
        if theta < math.pi:
            return -math.cos(rod_to_crank_angle) * force_parallel_to_rod
        else:
            return math.cos(rod_to_crank_angle) * force_parallel_to_rod
    
    def run_simulation(self, num_cycles=2, num_points=1000):
        """
        Run the torque simulation over specified engine cycles.
        
        Parameters:
            num_cycles (int): Number of 4-stroke cycles to simulate.
            num_points (int): Number of sample points per cycle.
        
        Returns:
            tuple: (theta_degrees, torque_values)
        """
        theta_start = 0  # Changed from -1 to 0
        theta_end = 4 * math.pi * num_cycles  # 4pi radians per 4-stroke cycle
        theta_values = np.linspace(theta_start, theta_end, num_cycles * num_points)
        torque_values = []
    
        # Initialize angular velocity
        angular_velocity = self.crank.angular_velocity  # Assuming Crank has an attribute angular_velocity
    
        for i, theta in enumerate(theta_values):
            # Calculate delta_theta and corresponding dt
            if angular_velocity != 0:
                if i == 0:
                    delta_theta = theta_values[1] - theta_values[0]
                else:
                    delta_theta = theta_values[i] - theta_values[i - 1]
                dt = delta_theta / angular_velocity
            else:
                dt = 0.001  # Prevent division by zero; arbitrary small value
    
            # Calculate force using GasSimulation
            force = self.gas_sim.calculate_force(theta, dt)
    
            # Debug: Print force and theta
            # print(f"Theta: {theta:.2f} rad, Force: {force:.2f} N")
    
            # If force calculation is returning None or invalid values, skip
            if not isinstance(force, (int, float)):
                torque_values.append(0)
                continue
    
            # Find rod direction vector
            rod_direction_vector = self.find_rod_direction_vector(theta)
    
            # Transfer force to rod
            force_parallel_to_rod = self.transfer_force_to_rod(force, rod_direction_vector)
    
            # Transfer force to crank
            force_tangent_to_crank = self.transfer_force_to_crank(force_parallel_to_rod, rod_direction_vector, theta)
    
            # Calculate torque using Crank
            torque = self.crank.get_torque(force_tangent_to_crank)
    
            # Debug: Print torque
            # print(f"Theta: {theta:.2f} rad, Torque: {torque:.2f} Nm")
    
            # Store the torque value
            torque_values.append(torque)
    
            # Update angular velocity based on the torque
            self.crank.update_angular_velocity(torque, dt)
            angular_velocity = self.crank.angular_velocity  # Update for the next iteration
    
            # Debug: Print angular velocity
            # print(f"Angular Velocity: {angular_velocity:.2f} rad/s")
    
        # Convert theta from radians to degrees for plotting
        theta_degrees = np.degrees(theta_values)
    
        return theta_degrees, torque_values

def main():
    # Initialize the test simulation with arbitrary radius and mass values
    test_sim = TestTorqueSimulation(radius=0.1, mass=1.0)  # Radius in meters, mass in kg
    
    # Run the simulation
    theta_degrees, torque_values = test_sim.run_simulation(num_cycles=2, num_points=1000)
    
    # Debug: Check if torque_values are populated correctly
    # print(f"Number of torque values: {len(torque_values)}")
    # print(f"First 10 torque values: {torque_values[:10]}")
    
    # Handle case where torque_values might be empty
    if not torque_values:
        print("No torque values were calculated. Please check the simulation parameters and methods.")
        return
    
    # Plot torque vs. crank angle
    plt.figure(figsize=(12, 6))
    plt.plot(theta_degrees, torque_values, label='Torque', color='blue')
    plt.xlabel('Crank Angle (Degrees)')
    plt.ylabel('Torque (N·m)')
    plt.title('Torque vs. Crank Angle for a 4-Stroke Engine Cycle')
    plt.legend()
    plt.grid(True)
    plt.xlim(theta_degrees.min(), theta_degrees.max())
    
    # Adjust y-axis limits based on actual torque values
    min_torque = min(torque_values)
    max_torque = max(torque_values)
    plt.ylim(min_torque - 10, max_torque + 10)  # Adjust y-axis for better visibility
    
    plt.show()

if __name__ == "__main__":
    main()