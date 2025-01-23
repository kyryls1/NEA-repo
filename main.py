import pyglet
import math
import mechanicalComponents
import time
from vector import Vector
from renderer import Renderer
import sqlite3
import widgets

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

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        kwargs.update({'width': 1200, 'height': 720, 'resizable': False})
        super().__init__(*args, **kwargs)
        self.static_batch = pyglet.graphics.Batch()
        self.simulation_batch = pyglet.graphics.Batch()
        self.renderer = Renderer(self.simulation_batch, Vector(0, 0), 0, 0, 0)
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
            widgets.TextBox("Crank Radius:", ui_start_x, ui_start_y, textbox_width, self.static_batch),
            widgets.TextBox("Crank Mass:", ui_start_x, ui_start_y - ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Connecting Rod Length:", ui_start_x, ui_start_y - 2 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Connecting Rod Mass:", ui_start_x, ui_start_y - 3 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Piston Radius:", ui_start_x, ui_start_y - 4 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Piston Mass:", ui_start_x, ui_start_y - 5 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Configuration Name:", ui_start_x, ui_start_y - 6 * ui_spacing, textbox_width, self.static_batch)
        ]

        buttons_y = ui_start_y - 7 * ui_spacing - 20
        button_width = 180  # Width for buttons
        button_height = 50  # Height for buttons
        button_spacing = 20
        self.button_widgets = [
            widgets.Button("Pause/Unpause", ui_start_x, buttons_y, button_width, button_height, 
                   self.toggle_simulation_pause_button, self.static_batch),
            widgets.Button("Start Simulation", ui_start_x + button_width + button_spacing, buttons_y, 
                   button_width, button_height, self.start_simulation_button, self.static_batch),
            widgets.Button("Save Parameters", ui_start_x, buttons_y - button_height - button_spacing, 
                   button_width, button_height, self.save_parameters_button, self.static_batch),
            widgets.Button("Delete Record", ui_start_x + button_width + button_spacing, 
                           buttons_y - button_height - button_spacing, button_width, button_height, self.delete_record_button, self.static_batch)
        ]
        
        list_y = buttons_y - button_height - button_spacing * 2
        self.list_box = widgets.ListBox(self.get_engine_design_entries(), x=ui_start_x, y=list_y - 200, 
                                        width=button_width * 2 + button_spacing, height=200, batch=self.static_batch)

        self.text_cursor = self.get_system_mouse_cursor('text')
        self.focused_widget = None

    def on_draw(self):
        self.clear()
        self.static_batch.draw()
        self.fps_display.draw()
        self.simulation_batch.draw()

    def update_simulation(self, dt):
        if not self.simulation_paused:
            self.simulation.update_all(dt)
            self.store_graph(self.simulation.crank.instantenous_torque)
            self.renderer.render(self.simulation.crank, self.simulation.connector_rod, self.simulation.piston)
            #self.simulation_update_count += 1
        '''
        current_time = time.time()

        if current_time - self.last_update_time >= 1:
            #print(f"Simulation updates per second: {self.simulation_update_count}")
            self.simulation_update_count = 0 
            self.last_update_time = current_time
'''
    def store_graph(self, torque):
        current_time = time.perf_counter() - self.start_time - self.elapsed_pause_time
        # Only store points if enough time has passed (reduce sampling rate)
        if not hasattr(self, 'last_store_time') or current_time - self.last_store_time >= 0.001:  # Store at 1000Hz
            self.renderer.store_graph_point((current_time, torque))
            self.last_store_time = current_time

    def save_parameters_button(self):
        if hasattr(self, 'simulation_parameters'): 
            configuration_name = self.widgets[6].document.text
            if configuration_name:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                if self.button_widgets[2].label.text == "Overwrite Parameters":
                    # Delete old record and related data
                    self.delete_record(cursor, self.last_save_id)
                    conn.commit()  # Commit deletion before proceeding
                    self.list_box.update_table(self.get_engine_design_entries())  # Update UI to reflect deletion
                else:
                    self.button_widgets[2].label.text = "Overwrite Parameters"
                
                # Save new record
                self.save_configuration(cursor, configuration_name, *self.simulation_parameters)
                self.last_save_id = cursor.lastrowid
                self.save_torque_time_data(cursor, self.last_save_id)
                self.save_paused_points(cursor, self.last_save_id)
                
                conn.commit()
                conn.close()
                self.list_box.update_table(self.get_engine_design_entries())
                self.widgets[6].document.text = ""

    def save_configuration(self, cursor, configuration_name, *parameters):
        # First create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engine_designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                configuration_name TEXT,
                crank_radius REAL,
                crank_mass REAL,
                rod_length REAL,
                rod_mass REAL,
                piston_radius REAL,
                piston_mass REAL
            )
        ''')
        cursor.execute('''
            INSERT INTO engine_designs (
                timestamp, configuration_name, crank_radius, crank_mass, 
                rod_length, rod_mass, piston_radius, piston_mass
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (time.strftime("%H:%M:%S"), configuration_name, *parameters))

    def save_torque_time_data(self, cursor, engine_design_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS torque_time_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_design_id INTEGER,
                time REAL,
                torque REAL,
                FOREIGN KEY(engine_design_id) REFERENCES engine_designs(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_time ON torque_time_data(time)')
        cursor.execute('PRAGMA floating_point_numbers=ON')
        for time_point, torque_point in self.renderer.graph_points:
            cursor.execute('''
                INSERT INTO torque_time_data (engine_design_id, time, torque)
                VALUES (?, ?, ?)
            ''', (engine_design_id, round(time_point, 6), round(torque_point, 6)))

    def save_paused_points(self, cursor, engine_design_id):                    
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paused_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_design_id INTEGER,
                paused_time REAL,
                FOREIGN KEY(engine_design_id) REFERENCES engine_designs(id)
            )
        ''')
        for paused_time in self.renderer.paused_points:
            cursor.execute('''
                INSERT INTO paused_points (engine_design_id, paused_time)
                VALUES (?, ?)
            ''', (engine_design_id, paused_time))
        
    def delete_record_button(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        focused_row = self.list_box.get_focused_data()
        if focused_row is not None:
            focused_row_id = focused_row[0]
            if focused_row_id == self.last_save_id:
                self.button_widgets[2].label.text = "Save Parameters"
            self.delete_record(cursor, focused_row_id)
            conn.commit()
            conn.close()
            self.list_box.update_table(self.get_engine_design_entries())

    def delete_record(self, cursor, save_id):
            cursor.execute('DELETE FROM engine_designs WHERE id = ?', (save_id,))
            cursor.execute('DELETE FROM torque_time_data WHERE engine_design_id = ?', (save_id,))
            cursor.execute('DELETE FROM paused_points WHERE engine_design_id = ?', (save_id,))

    def get_engine_design_entries(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_designs'")
        if cursor.fetchone() is not None:
            cursor.execute('SELECT id, timestamp, configuration_name FROM engine_designs')
            entries = cursor.fetchall()
            conn.close()
            return entries
        else:
            conn.close()
            return []

    def load_torque_time_data(self, engine_design_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT time, torque FROM torque_time_data
            WHERE engine_design_id = ?
            ORDER BY time ASC
        ''', (engine_design_id,))
        data_points = cursor.fetchall()
        conn.close()
        return data_points

    def load_paused_points(self, engine_design_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT paused_time FROM paused_points
            WHERE engine_design_id = ?
            ORDER BY paused_time ASC
        ''', (engine_design_id,))
        paused_points = cursor.fetchall()
        conn.close()
        return [point[0] for point in paused_points]
    
    def load_plot(self, selected_record):
        engine_design_id = selected_record[0]
        print(engine_design_id)
        data_points = self.load_torque_time_data(engine_design_id)
        paused_points = self.load_paused_points(engine_design_id)
        times, torques = zip(*data_points)
        self.renderer.plot_comparison_torque(times, torques, paused_points)

    def start_simulation_button(self):
        parameters = [widget.document.text for widget in self.widgets[0:6]]
        if 0 in parameters or None in parameters: return # fix this
        self.simulation_parameters = list(map(float, parameters))
        if self.simulation_parameters[2] <= self.simulation_parameters[0]:
            print("Connector Rod Length cannot be smaller than Crank Radius")
            return

        self.renderer.close_plot()
            
        self.simulation_batch = pyglet.graphics.Batch()
        self.simulation = Simulation(*self.simulation_parameters)
        self.renderer = Renderer(self.simulation_batch, self.origin, 
                                 self.simulation_parameters[0], self.simulation_parameters[2], self.simulation_parameters[4])
        self.start_time = time.perf_counter()
        self.elapsed_pause_time = 0
        self.button_widgets[2].label.text = "Save Parameters"
        self.simulation_paused = False

    def toggle_simulation_pause_button(self):
        if hasattr(self, 'simulation'):
            self.simulation_paused = not self.simulation_paused
            if self.simulation_paused:
                self.time_paused = time.perf_counter()
                self.renderer.store_paused_point(self.time_paused - self.start_time - self.elapsed_pause_time)
                self.renderer.plot_torque()
                #self.plot_process = multiprocessing.Process(target=self.renderer.plot_torque)
                #self.plot_process.start()
            else:
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
        
    def cycle_focus(self, direction):
        if self.is_focused_widget_set():
            index = self.widgets.index(self.focused_widget)
            new_index = (index + direction) % len(self.widgets)
        else:
            new_index = 0

        self.focus_widget(self.widgets[new_index])

    def on_mouse_motion(self, x, y, _dx, _dy):
        for widget in self.widgets:
            if widget.is_mouseover(x, y):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)
            for button_widget in self.button_widgets:
                button_widget.set_hover(x, y)
            else:
                self.list_box.on_mouse_motion(x, y)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.list_box.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            selected_data = self.list_box.on_mouse_press(x, y)
            if selected_data:
                print(f"Selected design: {selected_data[2]}")  # Print name of selected design
                self.load_plot(selected_data)
            
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
            if self.focused_widget is not self.widgets[6]:
                allowed_chars = "0123456789."
                if text not in allowed_chars:
                    return
                if text == "." and "." in self.focused_widget.document.text:
                    return
            else:
                if text == " " and self.focused_widget.document.text == "":
                    return
                elif len(self.focused_widget.document.text) >= 20:
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
            self.toggle_simulation_pause_button()

        if symbol == pyglet.window.key.TAB:
            direction = -1 if (modifiers & pyglet.window.key.MOD_SHIFT) else 1
            self.cycle_focus(direction)

        elif symbol == pyglet.window.key.ENTER:
            if self.is_focused_widget_set():

                self.cycle_focus(1)

if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    #cursor.execute("DROP TABLE IF EXISTS engine_designs")
    #cursor.execute("DROP TABLE IF EXISTS torque_time_data")
    #cursor.execute("DROP TABLE IF EXISTS paused_points")
    conn.commit()
    conn.close()
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable = True, vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/3000) 
    #pyglet.options['com_mta'] = True
    pyglet.app.run(interval=1/60)
