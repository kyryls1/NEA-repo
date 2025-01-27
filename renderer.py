import pyglet
import math
from linked_list import LinkedList
import matplotlib
import matplotlib.pyplot as plt
import multiprocessing

class Renderer:
    def __init__(self, batch, origin, crank_radius_mm, rod_length_mm, piston_radius_mm, piston_length_mm):
        self.batch = batch
        self.origin = origin
        self.crank_radius = crank_radius_mm
        self.rod_length = rod_length_mm
        self.piston_radius = piston_radius_mm
        self.piston_length = piston_length_mm
        self.open_design_plots = {}

        self.axle = pyglet.shapes.Circle(x=origin.x, y=origin.y, radius=20, color=[201, 201, 201], batch=batch)
        self.crankarm = pyglet.shapes.Line(x=origin.x, y=origin.y, x2=origin.x, y2=origin.y + crank_radius_mm, 
                                           thickness=40, color=[255, 255, 255], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius_mm, 
                                                  radius=20, color=[255, 255, 255], batch=batch)        
        self.piston = pyglet.shapes.Rectangle(x=origin.x - piston_radius_mm, 
                                              y=origin.y + crank_radius_mm + rod_length_mm, 
                                              width=piston_radius_mm * 2, 
                                              height=piston_length_mm, 
                                              color=[255, 255, 255], 
                                              batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius_mm + rod_length_mm, 
                                                   radius=15, color=[201, 201, 201], batch=batch)
        self.rod = pyglet.shapes.Line(x=origin.x, y=origin.y + crank_radius_mm, x2=origin.x, 
                                      y2=origin.y + crank_radius_mm + rod_length_mm, thickness=15, color=[201, 201, 201], batch=batch)
        
        self.graph_points = LinkedList()
        self.paused_points = LinkedList()
        self.throttle_change_points = LinkedList()  # New list for fuel changes
        matplotlib.use('TkAgg')
                                                  
    def render(self, crank, rod, piston):
        angle_degrees = math.degrees(crank.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.axle.rotation = angle_degrees

        self.rod.x = self.origin.x + rod.rod_start.x * 1000.0
        self.rod.y = self.origin.y + rod.rod_start.y * 1000.0
        self.rod.x2 = self.origin.x + rod.rod_end.x * 1000.0
        self.rod.y2 = self.origin.y + rod.rod_end.y * 1000.0

        self.crank_bearing.x = self.rod.x
        self.crank_bearing.y = self.rod.y
        self.piston_bearing.x = self.rod.x2
        self.piston_bearing.y = self.rod.y2

        self.piston.y = self.origin.y + piston.position.y * 1000

    def store_graph_point(self, current_time, torque, angular_velocity):
        self.graph_points.append((current_time, torque, angular_velocity))

    def store_paused_point(self, time):
        self.paused_points.append(time)

    def store_throttle_change_point(self, time, new_fuel_flow_rate):
        self.throttle_change_points.append((time, new_fuel_flow_rate))

    def plot_active_configuration(self, parameters):
        times, torques, angular_velocities = zip(*self.graph_points)
        paused_points = list(self.paused_points)
        throttle_changes = list(self.throttle_change_points)
        self.plot_performance(times, torques, angular_velocities, paused_points, throttle_changes, parameters)

    def plot_performance(self, times, torques, angular_velocities, paused_points, throttle_changes, simulation_parameters, engine_design_id=0):
        if engine_design_id in self.open_design_plots:
            if self.open_design_plots[engine_design_id].is_alive():
                print(f"Plot for engine design {engine_design_id} is already running")
                return
            else:
                del self.open_design_plots[engine_design_id]
        
        plot_process_comparison = multiprocessing.Process(
            target=self.run_plot, 
            args=(times, torques, angular_velocities, paused_points, throttle_changes, simulation_parameters)
        )
        self.open_design_plots[engine_design_id] = plot_process_comparison
        plot_process_comparison.start()

    @staticmethod
    def run_plot(times, torques, rpms, paused_points, throttle_changes, parameters):
        # Create figure with reduced height for parameter text
        fig, (ax_text, ax1, ax2) = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [0.15, 1, 1]})
        fig.canvas.manager.set_window_title(parameters[0])
        
        # Hide the ax_text axes
        ax_text.axis('off')
        
        # Format the simulation parameters with reduced font size and center alignment
        param_text = (
            f"Simulation Parameters\n"
            f"----------------------------------------\n"
            f"Crank:\n  Radius = {parameters[1]} mm  Mass = {parameters[2]} kg\n"
            f"Rod:\n  Length = {parameters[3]} mm  Mass = {parameters[4]} kg\n"
            f"Piston:\n  Radius = {parameters[5]} mm  Mass = {parameters[6]} kg"
        )
        
        # Add parameters text with a semi-transparent background box
        ax_text.text(
            0.5, 0.5, param_text,
            transform=ax_text.transAxes,
            family='monospace',
            fontsize=10,
            verticalalignment='center',
            horizontalalignment='center',
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5')
        )
        
        # Plot torque
        ax1.plot(times, torques, color='lightblue', linewidth=1)
        ax1.set_ylabel('Torque (N·m)')
        ax1.set_title('Crank Torque')
        ax1.grid(True, alpha=0.3)
        
        # Plot RPM
        ax2.plot(times, rpms, color='orange', linewidth=1)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Engine Speed (RPM)')
        ax2.set_title('Engine Speed')
        ax2.grid(True, alpha=0.3)
        
        # Add paused time indicators to both plots
        for time_point in paused_points:
            ax1.axvline(x=time_point, color='r', linestyle='--', alpha=0.5)
            ax2.axvline(x=time_point, color='r', linestyle='--', alpha=0.5)
            
        # Add throttle change indicators
        for time_point, fuel_mass in throttle_changes:
            ax1.axvline(x=time_point, color='g', linestyle='-.', alpha=0.5)
            ax2.axvline(x=time_point, color='g', linestyle='-.', alpha=0.5)
            ax1.text(time_point + 0.1, ax1.get_ylim()[1] * 0.9, 
                    f'Fuel: {fuel_mass:.3f}g', 
                    rotation=90, color='g')
            ax2.text(time_point + 0.1, ax2.get_ylim()[1] * 0.9,
                    f'Fuel: {fuel_mass:.3f}g',
                    rotation=90, color='g')
        
        plt.tight_layout(pad=2)  # Adjust spacing between subplots to reduce overall height
        plt.show()
        plt.close(fig) 

    def close_plot(self, engine_design_id):
        if engine_design_id in self.open_design_plots:
            process = self.open_design_plots[engine_design_id]
            if process.is_alive():
                process.terminate()
                process.join()
                print(f"Terminated plot for engine design {engine_design_id}")
            del self.open_design_plots[engine_design_id]