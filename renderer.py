import pyglet
import math
from linked_list import LinkedList
import matplotlib.pyplot as plt
import multiprocessing
from multiprocessing import Value
import ctypes

def run_plot(times, torques, paused_points, main_thread_blocked):
    plt.plot(times, torques, color='lightblue')
    plt.xlabel('Time (s)')
    plt.ylabel('Torque (N·m)')
    plt.title('Crank Torque')
    for time in paused_points:
        plt.axvline(x=time, color='r', linestyle='--', alpha=0.5)

    plt.show()

    main_thread_blocked.set()

class Renderer:
    def __init__(self, batch, origin, crank_radius, rod_length, piston_radius):
        self.main_thread_blocked = multiprocessing.Event()
        self.batch = batch
        self.origin = origin
        self.crank_radius = crank_radius
        self.rod_length = rod_length
        self.piston_radius = piston_radius

        self.axle = pyglet.shapes.Circle(x=origin.x, y=origin.y, radius=20, color=[201, 201, 201], batch=batch)
        self.crankarm = pyglet.shapes.Line(x=origin.x, y=origin.y, x2=origin.x, y2=origin.y + crank_radius, 
                                           thickness=40, color=[255, 255, 255], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius, 
                                                  radius=20, color=[255, 255, 255], batch=batch)        
        self.piston = pyglet.shapes.Rectangle(x=origin.x - piston_radius, y=origin.y + crank_radius + rod_length, 
                                              width=piston_radius * 2, height=150, color=[255, 255, 255], batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=origin.x, y=origin.y + crank_radius + rod_length, 
                                                   radius=15, color=[201, 201, 201], batch=batch)
        self.rod = pyglet.shapes.Line(x=origin.x, y=origin.y + crank_radius, x2=origin.x, 
                                      y2=origin.y + crank_radius + rod_length, thickness=15, color=[201, 201, 201], batch=batch)
        
        self.graph_points = LinkedList()
        self.paused_points = LinkedList()
                                                  
    def render(self, crank, rod, piston):
        crank_x = self.origin.x
        crank_y = self.origin.y

        angle_degrees = math.degrees(crank.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.axle.rotation = angle_degrees

        self.rod.x = crank_x + rod.rod_start.x
        self.rod.y = crank_y + rod.rod_start.y
        self.rod.x2 = crank_x + rod.rod_end.x
        self.rod.y2 = crank_y + rod.rod_end.y

        self.crank_bearing.x = self.rod.x
        self.crank_bearing.y = self.rod.y
        self.piston_bearing.x = self.rod.x2
        self.piston_bearing.y = self.rod.y2

        self.piston.x = crank_x - piston.RADIUS
        self.piston.y = crank_y + piston.position.y

    def store_graph_point(self, point):
        self.graph_points.append(point)

    def store_paused_point(self, time):
        self.paused_points.append(time)

    def plot_torque(self):
        times = [t[0] for t in self.graph_points]
        torques = [t[1] for t in self.graph_points]
        paused_times = list(self.paused_points)
        
        self.main_thread_blocked.clear()
        self.plot_process = multiprocessing.Process(target=run_plot, args=(times, torques, paused_times, self.main_thread_blocked))
        self.plot_process.start()
        self.main_thread_blocked.wait()

    def close_plot(self):
        self.plot_process.terminate()
        plt.close()
        self.main_thread_blocked[0] = False