import pyglet
import math
from linked_list import LinkedList
import matplotlib.pyplot as plt
import multiprocessing

class Renderer:
    def __init__(self, batch, origin, crank_radius_mm, rod_length_mm, piston_radius_mm):
        self.batch = batch
        self.origin = origin
        self.crank_radius = crank_radius_mm
        self.rod_length = rod_length_mm
        self.piston_radius = piston_radius_mm

        self.axle = pyglet.shapes.Circle(x=origin.x, y=origin.y, radius=20, color=[201, 201, 201], batch=batch)
        self.crankarm = pyglet.shapes.Line(x=origin.x, y=origin.y, x2=origin.x, y2=origin.y + crank_radius_mm, 
                                           thickness=40, color=[255, 255, 255], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius_mm, 
                                                  radius=20, color=[255, 255, 255], batch=batch)        
        self.piston = pyglet.shapes.Rectangle(x=origin.x - piston_radius_mm, y=origin.y + crank_radius_mm + rod_length_mm, 
                                              width=piston_radius_mm * 2, height=150, color=[255, 255, 255], batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius_mm + rod_length_mm, 
                                                   radius=15, color=[201, 201, 201], batch=batch)
        self.rod = pyglet.shapes.Line(x=origin.x, y=origin.y + crank_radius_mm, x2=origin.x, 
                                      y2=origin.y + crank_radius_mm + rod_length_mm, thickness=15, color=[201, 201, 201], batch=batch)
        
        self.graph_points = LinkedList()
        self.paused_points = LinkedList()
                                                  
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

    def store_graph_point(self, point):
        self.graph_points.append(point)

    def store_paused_point(self, time):
        self.paused_points.append(time)

    def plot_torque(self):
        times = [t[0] for t in self.graph_points]
        torques = [t[1] for t in self.graph_points]
        paused_times = list(self.paused_points)

        self.plot_process = multiprocessing.Process(target=self.run_plot, args=(times, torques, paused_times))
        self.plot_process.start()

    @staticmethod
    def run_plot(times, torques, paused_points):
        plt.plot(times, torques, color='lightblue')
        plt.xlabel('Time (s)')
        plt.ylabel('Torque (N·m)')
        plt.title('Crank Torque')
        for time in paused_points:
            plt.axvline(x=time, color='r', linestyle='--', alpha=0.5)

        plt.show()

    def close_plot(self):
        self.plot_process.terminate()
        plt.close()