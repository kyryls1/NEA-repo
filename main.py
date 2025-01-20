import pyglet
import math
import mechanicalComponents
import time
from vector import Vector
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import multiprocessing
from renderer import Renderer

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
    def __init__(self, crank_radius, crank_mass, connectorRod_length, rod_mass, piston_radius, piston_mass): 
        self.crank = mechanicalComponents.Crank(crank_radius, crank_mass)
        self.piston = mechanicalComponents.Piston(piston_mass,  piston_radius, crank_radius + connectorRod_length)
        self.connector_rod = mechanicalComponents.ConnectorRod(rod_mass, connectorRod_length, crank_radius)

        self.component_weight = (rod_mass + piston_mass) * 9.81
        self.gas_simulation = GasSimulation()
 
    def update_all(self, dt):
        gas_force = self.gas_simulation.calculate_force(self.crank.angle_radians, dt)
        total_force = gas_force + self.component_weight
        rod_direction_vector = self.find_rod_direction_vector()
        force_parallel_to_rod = self.transfer_force_to_rod(total_force, rod_direction_vector)
        force_tangent_to_crank = self.transfer_force_to_crank(force_parallel_to_rod, rod_direction_vector)

        self.crank.update(force_tangent_to_crank, dt)
        self.connector_rod.update(self.crank.calculate_delta_theta(dt))
        self.piston.update(self.connector_rod.rod_end.y)
 
    def find_normal_to_crank_motion(self, theta):
        if theta == math.pi/2:
            return Vector(0, 1)
        else:
            return Vector(1, math.tan(theta))
   
    def find_rod_direction_vector(self):
        return Vector(self.connector_rod.rod_end.x - self.connector_rod.rod_start.x, self.connector_rod.rod_end.y - self.connector_rod.rod_start.y) #this naming convention looks so stupid
    
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
        
class Button:
    def __init__(self, label, x, y, width, height, callback, batch):
        label_x = x + width/2
        label_y = y + height/2
        self.label = pyglet.text.Label(label, label_x, label_y, anchor_x='center', anchor_y='center', color = (0, 0, 0), batch=batch)
        self.bounding_box = pyglet.shapes.Rectangle(x, y, width, height, color=(200, 200, 220), batch=batch)
        self.callback = callback

    def is_mouseover(self, x, y):
        is_within_horizontal_bounds = self.bounding_box.x < x < self.bounding_box.x + self.bounding_box.width
        is_within_vertical_bounds = self.bounding_box.y < y < self.bounding_box.y + self.bounding_box.height

        return is_within_horizontal_bounds and is_within_vertical_bounds

    def on_click(self):
        self.callback()
        
class TextBox:
    def __init__(self, label, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument()
        self.label = pyglet.text.Label(label, x=x - 10, y=y, anchor_x='right', anchor_y='bottom', batch=batch)

        font_size = self.document.get_font()
        height = font_size.ascent - font_size.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, x, y, 0, width, height, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        padding = 2
        self.textbox_background = pyglet.shapes.Rectangle(x - padding, y - padding, width + padding, height + padding, color=(200, 200, 220), batch=batch)

    def is_mouseover(self, x, y):
        horizontal_distance = x - self.layout.x
        vertical_distance = y - self.layout.y

        is_within_horizontal_bounds = 0 < horizontal_distance < self.layout.width
        is_within_vertical_bounds = 0 < vertical_distance < self.layout.height

        return is_within_horizontal_bounds and is_within_vertical_bounds
    
    def set_focus(self):
        self.caret.visible = True
        self.caret.position = len(self.document.text)

    def clear_focus(self):
        self.caret.visible = False

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        kwargs.update({'width': 1200, 'height': 720, 'resizable': False})
        super().__init__(*args, **kwargs)
        self.static_batch = pyglet.graphics.Batch()
        self.simulation_paused = True
        self.fps_display = pyglet.window.FPSDisplay(self)

        #self.pool = multiprocessing.Pool()

        #self.simulation_update_count = 0

        self.origin = Vector(300, 200)
        simulation_area_width = 700  # Width allocated for simulation on the left
        ui_start_x = simulation_area_width + 50  # Starting X position for UI elements
        ui_start_y = 650  # Starting Y position for the topmost UI element
        ui_spacing = 50  # Vertical spacing between UI elements
        textbox_width = 70

        self.widgets = [
            TextBox("Crank Radius:", ui_start_x, ui_start_y, textbox_width, self.static_batch),
            TextBox("Crank Mass:", ui_start_x, ui_start_y - ui_spacing, textbox_width, self.static_batch),
            TextBox("Connecting Rod Length:", ui_start_x, ui_start_y - 2 * ui_spacing, textbox_width, self.static_batch),
            TextBox("Connecting Rod Mass:", ui_start_x, ui_start_y - 3 * ui_spacing, textbox_width, self.static_batch),
            TextBox("Piston Radius:", ui_start_x, ui_start_y - 4 * ui_spacing, textbox_width, self.static_batch),
            TextBox("Piston Mass", ui_start_x, ui_start_y - 5 * ui_spacing, textbox_width, self.static_batch)
        ]

        buttons_y = ui_start_y - 6 * ui_spacing - 20
        button_width = 180  # Width for buttons
        button_height = 50  # Height for buttons
        button_spacing = 20
        self.button_widgets = [
            Button("Pause/Unpause", ui_start_x, buttons_y, button_width, button_height, 
                   self.toggle_simulation_pause, self.static_batch),
            Button("Start Simulation", ui_start_x + button_width + button_spacing, buttons_y, 
                   button_width, button_height, self.start_simulation, self.static_batch)
        ]

        self.text_cursor = self.get_system_mouse_cursor('text')
        self.focused_widget = None

    def on_draw(self):
        self.clear()
        self.static_batch.draw()
        self.fps_display.draw()
        if hasattr(self, 'simulation'):
            if not self.simulation_paused: 
                self.renderer.render(self.simulation.crank, self.simulation.connector_rod, self.simulation.piston)
            self.simulation_batch.draw()

    def store_graph(self, torque):
        current_time = time.perf_counter() - self.start_time - self.elapsed_pause_time
        self.renderer.store_graph_point((current_time, torque))

    def update_simulation(self, dt):
        if not self.simulation_paused:
            self.simulation.update_all(dt)
            self.store_graph(self.simulation.crank.instantenous_torque)
            #self.simulation_update_count += 1
        '''
        current_time = time.time()

        if current_time - self.last_update_time >= 1:
            #print(f"Simulation updates per second: {self.simulation_update_count}")
            self.simulation_update_count = 0 
            self.last_update_time = current_time
'''
    def start_simulation(self):
        parameters = [widget.document.text for widget in self.widgets]
        self.simulation_parameters = list(map(float, parameters))
        if self.simulation_parameters[2] <= self.simulation_parameters[0]:
            print("Connector Rod Length cannot be smaller than Crank Radius")
            return

        self.simulation_batch = pyglet.graphics.Batch()
        self.simulation = Simulation(*self.simulation_parameters)
        self.renderer = Renderer(self.simulation_batch, self.origin, 
                                 self.simulation_parameters[0], self.simulation_parameters[2], self.simulation_parameters[4])
        plt.close()
        self.start_time = time.perf_counter()
        self.elapsed_pause_time = 0
        self.simulation_paused = False

    def toggle_simulation_pause(self):
        if hasattr(self, 'simulation'):
            self.simulation_paused = not self.simulation_paused
            if self.simulation_paused:
                self.time_paused = time.perf_counter()
                self.renderer.store_paused_point(self.time_paused - self.start_time - self.elapsed_pause_time)
                self.renderer.plot_torque()
                #self.plot_process = multiprocessing.Process(target=self.renderer.plot_torque)
                #self.plot_process.start()
            else:
                # If a Matplotlib window is still open, close it
                #self.plot_process.terminate()
                time_resumed = time.perf_counter()
                self.elapsed_pause_time += time_resumed - self.time_paused
                self.renderer.close_plot()

    def is_focused_widget_set(self):
        return self.focused_widget is not None

    def focus_widget(self, widget):
        if self.is_focused_widget_set():
            self.focused_widget.clear_focus()
        widget.set_focus()
        self.focused_widget = widget
        
    def on_mouse_motion(self, x, y, _dx, _dy):
        for widget in self.widgets:
            if widget.is_mouseover(x, y):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        #if not hasattr(self, 'renderer'):
            if button == pyglet.window.mouse.LEFT:
                for button_widget in self.button_widgets:
                    if button_widget.is_mouseover(x, y):
                        button_widget.on_click()
                        return

                for widget in self.widgets:
                    if widget.is_mouseover(x, y):
                        if self.focused_widget == widget:
                            break
                        else:
                            self.focus_widget(widget)
                            break
                else:
                    if self.is_focused_widget_set():
                        self.focused_widget.clear_focus()
                        self.focused_widget = None

                if self.is_focused_widget_set():
                    self.focused_widget.caret.on_mouse_press(x, y, button_widget, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.is_focused_widget_set():
            self.focused_widget.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if text in ("\r", "\n"):
            return
        if self.is_focused_widget_set():
            allowed_chars = "0123456789."
            if text not in allowed_chars:
                return
            if text == "." and "." in self.focused_widget.document.text:
                return
            
            self.focused_widget.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.is_focused_widget_set():
            self.focused_widget.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.is_focused_widget_set():
            self.focused_widget.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.P:
            self.toggle_simulation_pause()

        if symbol == pyglet.window.key.TAB:
            direction = -1 if (modifiers & pyglet.window.key.MOD_SHIFT) else 1
            self.cycle_focus(direction)

        elif symbol == pyglet.window.key.ENTER:
            if self.is_focused_widget_set():

                self.cycle_focus(1)

    def cycle_focus(self, direction):
        if self.is_focused_widget_set():
            index = self.widgets.index(self.focused_widget)
            new_index = (index + direction) % len(self.widgets)
        else:
            new_index = 0

        self.focus_widget(self.widgets[new_index])

if __name__ == "__main__":
    multiprocessing.freeze_support()
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable = True, vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/3000) 
    #pyglet.options['com_mta'] = True
    pyglet.app.run(interval=1/60)
