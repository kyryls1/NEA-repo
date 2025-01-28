import pyglet
import time
from vector import Vector
from renderer import Renderer
from simulation import Simulation
import sqlite3
import widgets
import math

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_batch = pyglet.graphics.Batch()
        self.simulation_batch = pyglet.graphics.Batch()
        self.renderer = Renderer(self.simulation_batch, Vector(0, 0), 0, 0, 0, 0)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.simulation_paused = True
        self.engine_stalled = True
        self.last_save_id = None
        self.simulation_speed_factor = 0.02  # 50x slower
        self.origin = Vector(300, 200)

        simulation_area_width = 600
        ui_start_x = simulation_area_width + 100
        ui_start_y = 750
        ui_spacing = 40
        textbox_width = 100

        self.labels = [
            pyglet.text.Label("Fuel Flow Rate", x=ui_start_x, y=ui_start_y,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Crank", x=ui_start_x, y=ui_start_y - 2 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Connecting Rod", x=ui_start_x, y=ui_start_y - 5 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Piston", x=ui_start_x, y=ui_start_y - 8 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Manage Saves", x=ui_start_x, y=ui_start_y - 13 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch)
        ]

        self.parameter_input_widgets = [
            #Fuel Flow Rate
            widgets.TextBox("Fuel injected per cycle (g):", ui_start_x, ui_start_y - ui_spacing, textbox_width, self.static_batch),
            # Crank
            widgets.TextBox("Radius (mm):", ui_start_x, ui_start_y - 3 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 4 * ui_spacing, textbox_width, self.static_batch),
            # Connecting Rod
            widgets.TextBox("Length (mm):", ui_start_x, ui_start_y - 6 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 7 * ui_spacing, textbox_width, self.static_batch),
            # Piston
            widgets.TextBox("Radius (mm):", ui_start_x, ui_start_y - 9 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Length (mm):", ui_start_x, ui_start_y - 10 * ui_spacing, textbox_width, self.static_batch), 
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 11 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Deck Clearance (mm):", ui_start_x, ui_start_y - 12 * ui_spacing, textbox_width, self.static_batch),
            #Manage Saves
            widgets.TextBox("Configuration Name:", ui_start_x, ui_start_y - 14 * ui_spacing, textbox_width, self.static_batch)
        ]

        buttons_y = ui_start_y - 15 * ui_spacing - 20
        button_width = 180
        button_height = 50
        button_spacing = 20
        self.button_widgets = [
            widgets.Button("Pause/Unpause", ui_start_x, buttons_y, button_width, button_height, 
                   self.toggle_simulation_pause_button, self.static_batch),
            widgets.Button("Set Parameters", ui_start_x + button_width + button_spacing, buttons_y, 
                   button_width, button_height, self.start_simulation_button, self.static_batch),
            widgets.Button("Starter", ui_start_x + 2 * (button_width + button_spacing), buttons_y, 
                   button_width, button_height, self.ignition_starter_button, self.static_batch),
            widgets.Button("Save Configuration", ui_start_x, buttons_y - button_height - button_spacing, 
                   button_width, button_height, self.save_config_button, self.static_batch),
            widgets.Button("Load Configuration", ui_start_x + button_width + button_spacing, 
                           buttons_y - button_height - button_spacing, button_width, button_height, self.load_config_button, self.static_batch),
            widgets.Button("Delete Record", ui_start_x + 2 * (button_width + button_spacing), 
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
        if not self.simulation_paused and not self.engine_stalled:
            scaled_dt = dt * self.simulation_speed_factor
            
            if self.simulation.crank.get_rpm() > self.simulation.gas_simulation.STARTING_RPM:
                self.simulation.gas_simulation.decompression_valve_open = False
            else:
                self.simulation.gas_simulation.decompression_valve_open = True
                
            self.simulation.update_all(scaled_dt)
            self.renderer.render(self.simulation.crank, self.simulation.connector_rod, self.simulation.piston)
            
            if self.simulation.crank.angular_velocity < 0:
                print("Stall")
                self.simulation.crank.angular_velocity = 0
                self.engine_stalled = True  # Set stalled state

    def sample_graph_point(self, _dt):
        if self.simulation_paused is True: 
            return
        current_time = (time.perf_counter() - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
        torque = round(self.simulation.crank.instantenous_torque, 6)
        rpm = round(self.simulation.crank.get_rpm(), 6)
        self.renderer.store_graph_point(current_time, torque, rpm)

    def update_fuel_flow_rate(self, fuel_flow_rate):
        if hasattr(self, 'simulation') and fuel_flow_rate != "":
            self.simulation.update_fuel_flow_rate(fuel_flow_rate)
            current_time = (time.perf_counter() - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
            self.renderer.store_throttle_change_point(current_time, fuel_flow_rate)

    def save_config_button(self):
        if hasattr(self, 'renderer_parameters'): 
            configuration_name = self.parameter_input_widgets[9].document.text
            if configuration_name:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                if self.button_widgets[3].label.text == "Overwrite Last Save":
                    self.delete_record(cursor, self.last_save_id)
                    conn.commit()
                    self.list_box.update_table(self.get_engine_design_entries())
                else:
                    self.button_widgets[3].label.text = "Overwrite Last Save"

                self.save_configuration(cursor, configuration_name, *self.renderer_parameters)
                self.last_save_id = cursor.lastrowid
                self.save_engine_performance_data(cursor, self.last_save_id)
                self.save_paused_points(cursor, self.last_save_id)
                self.save_throttle_change_points(cursor, self.last_save_id)
                conn.commit()
                conn.close()

                self.list_box.update_table(self.get_engine_design_entries())
                self.parameter_input_widgets[8].document.text = ""

    def load_config_button(self):
        parameters = list(self.list_box.get_focused_data())
        if parameters is not None:
            self.start_simulation(parameters[2:], self.origin)

    def save_configuration(self, cursor, configuration_name, *parameters):
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS engine_designs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    configuration_name VARCHAR(40),
                    crank_radius REAL,
                    crank_mass REAL,
                    rod_length REAL,
                    rod_mass REAL,
                    piston_radius REAL,
                    piston_length REAL,
                    deck_clearance REAL,
                    piston_mass REAL
                )
            ''')
        record_name = f"{time.strftime('%H:%M:%S')} | {configuration_name}"
        cursor.execute('''
                INSERT INTO engine_designs (
                    configuration_name, crank_radius, crank_mass, 
                    rod_length, rod_mass, piston_radius, piston_length, deck_clearance, piston_mass
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_name, *parameters))

    def save_engine_performance_data(self, cursor, engine_design_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engine_performance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_design_id INTEGER,
                torque REAL,
                rpm REAL,
                time REAL,
                FOREIGN KEY(engine_design_id) REFERENCES engine_designs(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS time_index ON engine_performance_data(time)')
        for time_point, torque_point, rpm in self.renderer.graph_points:
            cursor.execute('''
                INSERT INTO engine_performance_data (engine_design_id, torque, rpm, time)
                VALUES (?, ?, ?, ?)
            ''', (engine_design_id, torque_point, rpm, time_point))

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

    def save_throttle_change_points(self, cursor, engine_design_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS throttle_change_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_design_id INTEGER,
                time REAL,
                fuel_flow_rate REAL,
                FOREIGN KEY(engine_design_id) REFERENCES engine_designs(id)
            )
        ''')
        for time_point, fuel_flow_rate in self.renderer.throttle_change_points:
            cursor.execute('''
                INSERT INTO throttle_change_points (engine_design_id, time, fuel_flow_rate)
                VALUES (?, ?, ?)
            ''', (engine_design_id, time_point, fuel_flow_rate))
        
    def delete_record_button(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        focused_row = self.list_box.get_focused_data()
        if focused_row is not None:
            focused_row_id = focused_row[0]
            if focused_row_id == self.last_save_id:
                self.button_widgets[3].label.text = "Save Configuration"
            self.renderer.close_plot(focused_row_id)
            self.delete_record(cursor, focused_row_id)
            conn.commit()
            conn.close()
            self.list_box.update_table(self.get_engine_design_entries())

    def delete_record(self, cursor, save_id):
            cursor.execute('DELETE FROM engine_designs WHERE id = ?', (save_id,))
            cursor.execute('DELETE FROM engine_performance_data WHERE engine_design_id = ?', (save_id,))
            cursor.execute('DELETE FROM paused_points WHERE engine_design_id = ?', (save_id,))
            cursor.execute('DELETE FROM throttle_change_points WHERE engine_design_id = ?', (save_id,))

    def get_engine_design_entries(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_designs'")
            if cursor.fetchone() is not None:
                cursor.execute('SELECT id, configuration_name, crank_radius, crank_mass, rod_length, rod_mass, piston_radius, piston_length, deck_clearance, piston_mass FROM engine_designs')  # Explicitly list columns
                entries = cursor.fetchall()
            else:
                raise sqlite3.OperationalError("Table 'engine_designs' does not exist in the database")
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            entries = []
        except Exception as e:
            print(f"Unexpected error: {e}")
            entries = []
        finally:
            conn.close()
            return entries  

    def load_engine_performance_data(self, engine_design_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT time, torque, rpm FROM engine_performance_data
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
        ''', (engine_design_id,))
        paused_points = cursor.fetchall()
        conn.close()
        return [point[0] for point in paused_points]
    
    def load_throttle_change_points(self, engine_design_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT time, fuel_flow_rate FROM throttle_change_points
            WHERE engine_design_id = ?
        ''', (engine_design_id,))
        points = cursor.fetchall()
        conn.close()
        return points

    def load_plot(self, selected_record):
        engine_design_id = selected_record[0]
        data_points = self.load_engine_performance_data(engine_design_id)
        paused_points = self.load_paused_points(engine_design_id)
        throttle_changes = self.load_throttle_change_points(engine_design_id)
        times, torques, angular_velocities = zip(*data_points)
        self.renderer.plot_performance(times, torques, angular_velocities, paused_points, throttle_changes, selected_record[1:], engine_design_id)

    def start_simulation_button(self):
        inputs = [widget.document.text for widget in self.parameter_input_widgets[1:9]] #include only numerical config inputs
        if "" in inputs: 
            return
        parameters = list(map(float, inputs))
        if 0 in parameters:
            print("Parameters cannot be zero")
            return
        elif parameters[2] <= parameters[0]:
            print("Connector Rod Length cannot be smaller than Crank Radius")
            return
            
        self.renderer_parameters = parameters.copy()
        self.start_simulation(parameters, self.origin)

    def start_simulation(self, simulation_parameters, origin):
        self.renderer.close_plot(0)
        self.simulation_batch = pyglet.graphics.Batch()
        # [0]=crank_radius, [2]=rod_length, [4]=piston_radius, [5]=piston_length, [7]=deck_clearance
        renderer_parameters = simulation_parameters.copy()
        for i in [0, 2, 4, 5, 7]:
            simulation_parameters[i] = self.mm_to_m(simulation_parameters[i])

        self.simulation = Simulation(*simulation_parameters)
        self.renderer = Renderer(self.simulation_batch, origin, 
                                 renderer_parameters[0], renderer_parameters[2], 
                                 renderer_parameters[4], renderer_parameters[5])
        self.start_time = time.perf_counter()
        self.elapsed_pause_time = 0
        self.button_widgets[3].label.text = "Save Configuration"
        self.simulation_paused = False

    def toggle_simulation_pause_button(self):
        if hasattr(self, 'simulation'):
            self.simulation_paused = not self.simulation_paused
            if self.simulation_paused:
                self.time_paused = time.perf_counter()
                current_time = (self.time_paused - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
                self.renderer.store_paused_point(current_time)
                named_parameters = ["Active Configuration"] + self.renderer_parameters
                self.renderer.plot_active_configuration(named_parameters)
            else:
                time_resumed = time.perf_counter()
                self.elapsed_pause_time += time_resumed - self.time_paused
                self.renderer.close_plot(0)

    def ignition_starter_button(self):
        if hasattr(self, 'simulation') and self.simulation_paused is False:
            if self.engine_stalled:
                self.engine_stalled = False
                pyglet.clock.schedule_interval(self.starter, 0.01)
                pyglet.clock.schedule_once(self.starter_cutout, 1)

    def starter_cutout(self, _dt):
        pyglet.clock.unschedule(self.starter)

    def starter(self, _dt):
        starting_force = 50
        self.simulation.crank.update_angular_velocity(starting_force, _dt * self.simulation_speed_factor)
        print(f"Starter applied, current RPM: {self.simulation.crank.get_rpm()}")

    def mm_to_m(self, value):
        return value / 1000.0

    def m_to_mm(self, value):
        return value * 1000.0

    def get_database_entries(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_designs'")
        if cursor.fetchone() is not None:
            cursor.execute('SELECT configuration_name FROM engine_designs')
            entries = cursor.fetchall()
            conn.close()
            return [entry[0] for entry in entries]
        else:
            conn.close()
            return []

    def is_focused_widget_set(self):
        return self.focused_widget is not None

    def focus_widget(self, widget):
        if self.is_focused_widget_set():
            self.focused_widget.clear_focus()
        widget.set_focus()
        self.focused_widget = widget
        
    def cycle_focus(self, direction):
        if self.is_focused_widget_set():
            index = self.parameter_input_widgets.index(self.focused_widget)
            new_index = (index + direction) % len(self.parameter_input_widgets)
            if new_index == 0:
                new_index = 1
        else:
            new_index = 1

        self.focus_widget(self.parameter_input_widgets[new_index])

    def on_mouse_motion(self, x, y, _dx, _dy):
        for widget in self.parameter_input_widgets:
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
            print(selected_data)
            if selected_data:
                self.load_plot(selected_data)
            
            for button_widget in self.button_widgets:
                if button_widget.is_mouseover(x, y):
                    button_widget.on_click()
                    return

            for widget in self.parameter_input_widgets:
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
            if self.focused_widget is not self.parameter_input_widgets[9]:
                allowed_chars = "0123456789."
                if text not in allowed_chars:
                    return
                if text == "." and "." in self.focused_widget.document.text:
                    return
            else:
                if text == " " and self.focused_widget.document.text == "":
                    return
                elif len(self.focused_widget.document.text) >= 40:
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
                if self.focused_widget is self.parameter_input_widgets[0]:
                    self.update_fuel_flow_rate(float(self.focused_widget.document.text))
                    self.focused_widget.clear_focus()
                    self.focused_widget = None
                else:
                    self.cycle_focus(1)

if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    simulation = SimulationWindow(width=1280, height=900, resizable=False, caption="Piston Engine Simulation", vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/3000) 
    pyglet.clock.schedule_interval(simulation.sample_graph_point, 1/1000)
    #pyglet.options['com_mta'] = True
    pyglet.app.run(interval=1/60)
