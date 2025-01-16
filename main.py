import pyglet
import math
import crank, connectorRod, piston
import time
from vector import Vector


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
        if 0 <= theta <= math.pi:
            #print(self.t_max - (self.t_max - self.t_min) * (theta / math.pi))
            return self.t_max - (self.t_max - self.t_min) * (theta / math.pi)
        else:
            #print(self.t_min + (self.t_max - self.t_min) * ((theta - math.pi) / math.pi))
            return self.t_min + (self.t_max - self.t_min) * ((theta - math.pi) / math.pi)
        
    def get_gas_mol(self, theta):
        #print(math.degrees(theta))
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

        return math.cos(piston_to_rod_angle) * total_downward_force
 
    def transfer_force_to_crank(self, force, rod_direction_vector):
        normalised_angle = (-self.crank.angle_radians + math.pi/2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)

        if self.crank.angle_radians < math.pi:
            return -math.cos(rod_to_crank_angle) * force
        else:
            return math.cos(rod_to_crank_angle) * force
        
class TextWidget:
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, x, y, 0, width, height,
                                                               batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)
        # Rectangular outline
        pad = 2
        self.rectangle = pyglet.shapes.Rectangle(x - pad, y - pad, width + pad, height + pad,
                                                 color=(200, 200, 220), batch=batch)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)
        self.simulation = Simulation(1, 1, 1, 1, 1)
        self.fps_display = pyglet.window.FPSDisplay(self)

        self.simulation_update_count = 0
        self.last_update_time = time.time()

#work in progress text boxes

        self.batch2 = pyglet.graphics.Batch()

        self.labels = [
            pyglet.text.Label('Width', x=10, y=100, anchor_y='bottom',
                              color=(255, 255, 255, 255), batch=self.batch2),
            pyglet.text.Label('test', x=10, y=60, anchor_y='bottom',
                              color=(255, 255, 255, 255), batch=self.batch2),
            pyglet.text.Label('test2', x=10, y=20,
                              anchor_y='bottom', color=(255, 255, 255, 255),
                              batch=self.batch2),
        ]
        self.widgets = [
            TextWidget('This is a test', 200, 100, self.width - 210, self.batch2),
            TextWidget('This is a test', 200, 60, self.width - 210, self.batch2),
            TextWidget('This is a test', 200, 20, self.width - 210, self.batch2),
        ]
        self.text_cursor = self.get_system_mouse_cursor('text')

        self.focus = None
        self.set_focus(self.widgets[0])
        #work in progress

    def on_draw(self):
        self.clear()
        self.simulation.draw()
        self.fps_display.draw()
        #wip
        #pyglet.gl.glClearColor(1, 1, 1, 1)
        self.batch2.draw()
 
    def update_simulation(self, dt):
        self.simulation.update_all(dt)
        self.simulation_update_count += 1
        current_time = time.time()

        if current_time - self.last_update_time >= 1:
            #print(f"Simulation updates per second: {self.simulation_update_count}")
            self.simulation_update_count = 0  # Reset counter after printing
            self.last_update_time = current_time
    '''
    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        for widget in self.widgets:
            widget.width = width - 110
    '''
    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
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

        #elif symbol == pyglet.window.key.ESCAPE:
            #pyglet.app.exit()

        elif symbol == pyglet.window.key.ENTER:
            my_text = int(self.widgets[0].document.text)
            self.simulation = Simulation(1, 1, 1, 1, my_text)
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
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/1000)
    #pyglet.options['com_mta'] = True
    pyglet.app.run(interval=1/30)
