import pyglet
import math
from linked_list import LinkedList
import matplotlib
import matplotlib.pyplot as plt
import multiprocessing

class Renderer:
    def __init__(self, batch, origin, crank_radius_m, rod_length_m, piston_radius_m, piston_length_m):
        self.batch = batch
        self.origin = origin
        self.scale_factor = 2000  # 1mm = 2px
        self.open_design_plots = {}
        
        scaled_crank_px = crank_radius_m * self.scale_factor
        scaled_rod_px = rod_length_m * self.scale_factor
        scaled_piston_radius_px = piston_radius_m * self.scale_factor
        scaled_piston_length_px = piston_length_m * self.scale_factor
        
        self.rod = pyglet.shapes.Line(x=origin.x, y=origin.y + scaled_crank_px, x2=origin.x, 
                                      y2=origin.y + scaled_crank_px + scaled_rod_px, thickness=15, color=[201, 201, 201], batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + scaled_crank_px + scaled_rod_px, 
                                                   radius=15, color=[201, 201, 201], batch=batch)
        self.piston = pyglet.shapes.Rectangle(x=origin.x - scaled_piston_radius_px, 
                                              y=origin.y + scaled_crank_px + scaled_rod_px, 
                                              width=scaled_piston_radius_px * 2, 
                                              height=scaled_piston_length_px, 
                                              color=[255, 255, 255], 
                                              batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + scaled_crank_px, 
                                                  radius=20, color=[255, 255, 255], batch=batch)
        self.crankarm = pyglet.shapes.Line(x=origin.x, y=origin.y, x2=origin.x, y2=origin.y + scaled_crank_px, 
                                           thickness=40, color=[255, 255, 255], batch=batch)
        self.axle = pyglet.shapes.Circle(x=origin.x, y=origin.y, radius=20, color=[201, 201, 201], batch=batch)
        
        self.graph_points = LinkedList()
        self.paused_points = LinkedList()
        self.throttle_change_points = LinkedList()
        self.engine_load_change_points = LinkedList()
        matplotlib.use('TkAgg')
                                                  
    def render(self, crank, rod, piston):
        angle_degrees = math.degrees(crank.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.axle.rotation = angle_degrees

        self.rod.x = self.origin.x + rod.crank_anchor.x * self.scale_factor
        self.rod.y = self.origin.y + rod.crank_anchor.y * self.scale_factor
        self.rod.x2 = self.origin.x + rod.piston_anchor.x * self.scale_factor
        self.rod.y2 = self.origin.y + rod.piston_anchor.y * self.scale_factor

        self.crank_bearing.x = self.rod.x
        self.crank_bearing.y = self.rod.y
        self.piston_bearing.x = self.rod.x2
        self.piston_bearing.y = self.rod.y2

        self.piston.y = self.origin.y + piston.position.y * self.scale_factor

    def store_graph_point(self, current_time, torque, angular_velocity):
        self.graph_points.append((current_time, torque, angular_velocity))

    def store_paused_point(self, time):
        self.paused_points.append(time)

    def store_throttle_change_point(self, time, new_fuel_flow_rate):
        self.throttle_change_points.append((time, new_fuel_flow_rate))

    def store_engine_load_change_point(self, time, new_load):
        self.engine_load_change_points.append((time, new_load))

    def plot_active_configuration(self, parameters):
        time_points, torque_points, rpm_points = zip(*self.graph_points)
        paused_points = list(self.paused_points)
        throttle_changes = list(self.throttle_change_points)
        engine_load_changes = list(self.engine_load_change_points)
        self.plot_performance(time_points, torque_points, rpm_points, paused_points, throttle_changes, engine_load_changes, parameters)

    def plot_performance(self, time_points, torque_points, rpm_points, paused_points, throttle_changes, engine_load_changes, simulation_parameters, engine_design_id=0):
        if engine_design_id in self.open_design_plots:
            if self.open_design_plots[engine_design_id].is_alive():
                print(f"Warning: Plot for engine design is already open")
                return
            else:
                del self.open_design_plots[engine_design_id]
        
        plot_process_comparison = multiprocessing.Process(
            target=self.run_plot, 
            args=(time_points, torque_points, rpm_points, paused_points, throttle_changes, engine_load_changes, simulation_parameters)
        )
        self.open_design_plots[engine_design_id] = plot_process_comparison
        plot_process_comparison.start()

    @staticmethod
    def run_plot(times, torques, rpms, paused_points, throttle_changes, engine_load_changes, parameters):
        # Initial error handling to catch easily identifiable issues
        try:
            if not (len(times) == len(torques) == len(rpms)):
                raise ValueError("Mismatched lengths in plot data arrays")

            if not isinstance(parameters, (list, tuple)) or len(parameters) < 9:
                raise ValueError("Invalid parameters format")

        except Exception as e:
            print(f"Error plotting graph: {str(e)}")
            if 'process' in locals():
                process.terminate()
                process.join()

            return

        # Additional error handling to catch errors within data arrays
        try:
            fig, (config_parameters, torque_axis, rpm_axis) = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [0.15, 1, 1]})
            
            fig.canvas.manager.window.resizable(False, False)
            fig.canvas.manager.set_window_title(parameters[0])
            
            config_parameters.axis('off')
            configuration_parameters = (
                f"Simulation Parameters\n"
                f"Crank:  Radius = {parameters[1]} mm,  Mass = {parameters[2]} kg\n"
                f"Rod:  Length = {parameters[3]} mm,  Mass = {parameters[4]} kg\n"
                f"Piston:  Radius = {parameters[5]} mm,  Mass = {parameters[7]} kg,  Length = {parameters[6]} mm,  Deck Clearance = {parameters[8]} mm"
            )

            config_parameters.text(0.5, 0.5, configuration_parameters,
                transform=config_parameters.transAxes,
                fontsize=10,
                verticalalignment='center',
                horizontalalignment='center',
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5')
            )
            
            torque_axis.plot(times, torques, color='lightblue', linewidth=1, label='Torque')
            torque_axis.set_ylabel('Torque (N·m)')
            torque_axis.set_title('Engine Torque')
            torque_axis.grid(True, alpha=0.3)
            
            rpm_axis.plot(times, rpms, color='orange', linewidth=1, label='RPM')
            rpm_axis.set_xlabel('Time (s)')
            rpm_axis.set_ylabel('Engine Speed (RPM)')
            rpm_axis.set_title('Engine Speed')
            rpm_axis.grid(True, alpha=0.3)
            
            lines1, lines2 = [], []
            labels1, labels2 = [], []
            
            for time_point in paused_points:

                line1 = torque_axis.axvline(x=time_point, color='r', linestyle='--', alpha=0.5)
                line2 = rpm_axis.axvline(x=time_point, color='r', linestyle='--', alpha=0.5)
                if not lines1:
                    lines1.append(line1)
                    lines2.append(line2)
                    labels1.append('Simulation Paused')
                    labels2.append('Simulation Paused')
                
            for time_point, fuel_mass in throttle_changes:
                torque_axis.axvline(x=time_point, color='g', linestyle='-.', alpha=0.5)
                rpm_axis.axvline(x=time_point, color='g', linestyle='-.', alpha=0.5)
                torque_axis.annotate(
                    f'F: {fuel_mass}g',
                    xy=(time_point, 0.82),
                    xycoords=torque_axis.get_xaxis_transform(),
                    xytext=(5, 0),
                    textcoords='offset points',
                    rotation=90,
                    color='g',
                    va='center',
                    fontsize=8
                )
                rpm_axis.annotate(
                    f'F: {fuel_mass}g',
                    xy=(time_point, 0.82),
                    xycoords=rpm_axis.get_xaxis_transform(),
                    xytext=(5, 0),
                    textcoords='offset points',
                    rotation=90,
                    color='g',
                    va='center',
                    fontsize=8
                )

            for time_point, load in engine_load_changes:
                torque_axis.axvline(x=time_point, color='b', linestyle='-.', alpha=0.5)
                rpm_axis.axvline(x=time_point, color='b', linestyle='-.', alpha=0.5)
                torque_axis.annotate(
                    f'L: {load}W',
                    xy=(time_point, 0.82),
                    xycoords=torque_axis.get_xaxis_transform(),
                    xytext=(5, 0),
                    textcoords='offset points',
                    rotation=90,
                    color='b',
                    va='center',
                    fontsize=8
                )
                rpm_axis.annotate(
                    f'L: {load}W',
                    xy=(time_point, 0.82),
                    xycoords=rpm_axis.get_xaxis_transform(),
                    xytext=(5, 0),
                    textcoords='offset points',
                    rotation=90,
                    color='b',
                    va='center',
                    fontsize=8
                )

            plt.tight_layout()
            plt.show()
            plt.close(fig)
        except Exception as e:
            print(f"Error plotting graph: {str(e)}")
            if 'fig' in locals():
                plt.close(fig)
            if 'process' in locals():
                process.terminate()
                process.join()
                
            return

    def close_plot(self, engine_design_id):
        if engine_design_id in self.open_design_plots:
            process = self.open_design_plots[engine_design_id]
            if process.is_alive():
                process.terminate()
                process.join()
            del self.open_design_plots[engine_design_id]