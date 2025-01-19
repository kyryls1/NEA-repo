import pyglet
import math
import crank, connectorRod, piston
import time
from vector import Vector
import threading

class GasSimulation():
    def __init__(self):
        self.t_max = 2273
        self.t_min = 623
        self.mol_max = 0.748
        self.mol_min = 0.594
        self.vol_max = 0.5
        self.vol_min = 1
        self.t_difference = self.t_max - self.t_min

    def get_temperature(self, theta):
        if 0 <= theta < 0.1:
            return self.t_max

        elif 0.1 <= theta <= math.pi:
            k = 1.5 
            return self.t_min + (self.t_max - self.t_min) * math.exp(-k * (theta - 0.1))
        else:
            fraction = (theta - math.pi) / math.pi
            amplitude = 0.1 * (self.t_max - self.t_min)
            return self.t_min + amplitude * (1 - math.cos(math.pi * fraction))

    def get_gas_mol(self, theta):
        if 0 <= theta <= math.pi:
            #print(self.mol_max - (self.mol_max - self.mol_min) * (theta / math.pi))
            return self.mol_max - (self.mol_max - self.mol_min) * (theta / math.pi)
        else:
            #print(self.mol_max + (self.mol_max - self.mol_min) * ((theta - math.pi) / math.pi))
            return self.mol_min + (self.mol_max - self.mol_min) * ((theta - math.pi) / math.pi)
            
    def get_height(self, theta):
        # test func
        if 0 <= theta <= math.pi:
            return self.vol_max - (self.vol_max - self.vol_min) * (theta / math.pi)
        else:
            return self.vol_min + (self.vol_max - self.vol_min) * ((theta - math.pi) / math.pi)
        
    def calculate_force(self, theta, dt):
        temperature = self.get_temperature(theta)
        mols = self.get_gas_mol(theta)
        cylinder_height = self.get_height(theta)
        pressure = mols*8.31*temperature
        force = pressure/cylinder_height
        #print(force)
        return force

class Simulation():
    def __init__(self, radius, crank_mass, rod_mass, piston_mass, piston_radius, batch):
        self.batch = batch
 
        self.crank = crank.Crank(radius, crank_mass, batch)
        self.piston = piston.Piston(piston_mass,  piston_radius, batch)
        self.rod = connectorRod.ConnectorRod(rod_mass, batch)

        self.component_weight = (rod_mass + piston_mass) * 9.81
        self.gas_simulation = GasSimulation()
 
    def update_all(self, dt):
        force = self.gas_simulation.calculate_force(self.crank.angle_radians, dt)
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

        return total_downward_force/math.cos(piston_to_rod_angle)
 
    def transfer_force_to_crank(self, force, rod_direction_vector):
        normalised_angle = (-self.crank.angle_radians + math.pi/2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)

        if self.crank.angle_radians < math.pi:
            return -math.cos(rod_to_crank_angle) * force
        else:
            return math.cos(rod_to_crank_angle) * force
        
class TextBox:
    def __init__(self, label, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument()
        self.label = pyglet.text.Label(label, x=x, y=y, anchor_y='bottom', batch=batch)

        font_size = self.document.get_font()
        height = font_size.ascent - font_size.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, x+120, y, 0, width, height, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        padding = 2
        self.textbox_background = pyglet.shapes.Rectangle(x + 120 - padding, y - padding, width + padding, height + padding, color=(200, 200, 220), batch=batch)

    def is_mouseover(self, x, y):
        horizontal_distance = x - self.layout.x
        vertical_distance = y - self.layout.y

        is_within_horizontal_bounds = 0 < horizontal_distance < self.layout.width
        is_within_vertical_bounds = 0 < vertical_distance < self.layout.height

        return is_within_horizontal_bounds and is_within_vertical_bounds

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)
        self.batch = pyglet.graphics.Batch()
        self.simulation = Simulation(1, 1, 1, 1, 1, self.batch)
        self.paused = False
        self.fps_display = pyglet.window.FPSDisplay(self)

        self.simulation_update_count = 0
        self.last_update_time = time.time()

#work in progress text boxes
        self.widgets = [
            TextBox("Piston Radius/m",200, 100, 50, self.batch),
            TextBox("2", 200, 60, self.width - 210, self.batch),
            TextBox("4", 200, 20, self.width - 210, self.batch),
        ]
        self.text_cursor = self.get_system_mouse_cursor('text')

        self.focus = None
        self.set_focus(self.widgets[0])
        #work in progress

    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.fps_display.draw()
 
    def update_simulation(self, dt):
        if self.paused:
            return
        self.simulation.update_all(dt)
        self.simulation_update_count += 1
        current_time = time.time()

        if current_time - self.last_update_time >= 1:
            #print(f"Simulation updates per second: {self.simulation_update_count}")
            self.simulation_update_count = 0 
            self.last_update_time = current_time
    '''
    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        for widget in self.widgets:
            widget.width = width - 110
    '''
    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            if widget.is_mouseover(x, y):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.is_mouseover(x, y):
                self.set_focus(widget)
                break
        else:
            self.set_focus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.P:
            self.paused = not self.paused
            if self.paused:
                graph_thread = threading.Thread(target=self.simulation.crank.plot_torque)
                graph_thread.start()

        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                direction = -1
            else:
                direction = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                direction = 0

            self.set_focus(self.widgets[(i + direction) % len(self.widgets)])

        elif symbol == pyglet.window.key.ENTER:
            my_text = float(self.widgets[0].document.text)
            self.simulation = Simulation(1, 1, 1, 1, my_text, self.batch)
            self.widgets[0].document.text = ""

    def set_focus(self, focus):
        if focus is self.focus:
            return

        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True

if __name__ == "__main__":
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable = True, vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/3000)
    #pyglet.options['com_mta'] = True
    pyglet.app.run(interval=1/30)
