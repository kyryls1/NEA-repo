import pyglet
import time
from vector import Vector
from renderer import Renderer
from simulation import Simulation
import sqlite3
import widgets
import re

class SimulationWindow(pyglet.window.Window):
    PARAMETER_CONSTRAINTS = {
        'fuel_flow': {'min': 0, 'max': 1, 'name': 'Fuel flow rate'},
        'crank_radius': {'min': 15, 'max': 60, 'name': 'Crank radius'},
        'crank_mass': {'min': 1, 'max': 30, 'name': 'Crank mass'},
        'rod_length': {'min': 50, 'max': 140, 'name': 'Rod length'},
        'rod_mass': {'min': 0.5, 'max': 15, 'name': 'Rod mass'},
        'piston_radius': {'min': 17.5, 'max': 55, 'name': 'Piston radius'},
        'piston_length': {'min': 30, 'max': 70, 'name': 'Piston length'},
        'piston_mass': {'min': 1, 'max': 20, 'name': 'Piston mass'},
        'deck_clearance': {'min': 0.1, 'max': 5, 'name': 'Deck clearance'}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_batch = pyglet.graphics.Batch()
        self.simulation_batch = pyglet.graphics.Batch()
        self.renderer = Renderer(self.simulation_batch, Vector(0, 0), 0, 0, 0, 0)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.simulation_paused = True
        self.engine_stalled = True
        self.last_save_id = None
        self.simulation_speed_factor = 0.02  # 50x slower than real time
        self.origin = Vector(300, 350)

        simulation_area_width = 600
        ui_start_x = simulation_area_width + 150
        ui_start_y = self.height - 50
        ui_spacing = 40

        label_start_x = ui_start_x - 10
        self.labels = [
            pyglet.text.Label("Live Parameters", label_start_x, ui_start_y,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Crank", label_start_x, ui_start_y - 3 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Connecting Rod", label_start_x, ui_start_y - 6 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Piston", label_start_x, ui_start_y - 9 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch),
            pyglet.text.Label("Manage Saves", label_start_x, ui_start_y - 14 * ui_spacing,
                              color=(255, 255, 255, 255), batch=self.static_batch)
        ]

        textbox_width = 100
        self.parameter_input_widgets = [
            # Live Parameters
            widgets.TextBox("Fuel injected per cycle (g):", ui_start_x, ui_start_y - ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Engine load (W):", ui_start_x, ui_start_y - 2 * ui_spacing, textbox_width, self.static_batch),
            # Crank
            widgets.TextBox("Radius (mm):", ui_start_x, ui_start_y - 4 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 5 * ui_spacing, textbox_width, self.static_batch),
            # Connecting Rod
            widgets.TextBox("Length (mm):", ui_start_x, ui_start_y - 7 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 8 * ui_spacing, textbox_width, self.static_batch),
            # Piston
            widgets.TextBox("Radius (mm):", ui_start_x, ui_start_y - 10 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Length (mm):", ui_start_x, ui_start_y - 11 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Mass (kg):", ui_start_x, ui_start_y - 12 * ui_spacing, textbox_width, self.static_batch),
            widgets.TextBox("Deck Clearance (mm):", ui_start_x, ui_start_y - 13 * ui_spacing, textbox_width, self.static_batch),
            # Manage Saves
            widgets.TextBox("Configuration Name:", ui_start_x, ui_start_y - 15 * ui_spacing, 230, self.static_batch)
        ]

        buttons_y = ui_start_y - 17 * ui_spacing - 30
        buttons_x = 30
        button_width = 180
        button_height = 50
        button_spacing = 20
        self.button_widgets = [
            widgets.Button("Pause/Unpause", buttons_x, buttons_y, button_width, button_height,
                           self.toggle_simulation_pause_button, self.static_batch),
            widgets.Button("Set Parameters", buttons_x + button_width + button_spacing, buttons_y,
                           button_width, button_height, self.set_parameters_button, self.static_batch),
            widgets.Button("Starter", buttons_x + 2 * (button_width + button_spacing), buttons_y,
                           button_width, button_height, self.ignition_starter_button, self.static_batch),
            widgets.Button("Save Configuration", buttons_x, buttons_y - button_height - button_spacing,
                           button_width, button_height, self.save_config_button, self.static_batch),
            widgets.Button("Load Configuration", buttons_x + button_width + button_spacing,
                           buttons_y - button_height - button_spacing, button_width, button_height, self.load_config_button, self.static_batch),
            widgets.Button("Delete Record", buttons_x + 2 * (button_width + button_spacing),
                           buttons_y - button_height - button_spacing, button_width, button_height, self.delete_record_button, self.static_batch)
        ]

        self.text_cursor = self.get_system_mouse_cursor('text')
        self.focused_widget = None

        list_y = buttons_y - 115
        list_x = buttons_x + 3 * (button_width + button_spacing)
        self.record_table = widgets.ListTable(self.get_engine_design_entries(), x=list_x, y=list_y,
                                              width=button_width * 2 + button_spacing, height=210, batch=self.static_batch)

    # Text Widget Interaction
    def focus_widget(self, widget):
        if self.is_focused_widget_set():
            self.focused_widget.clear_focus()
        widget.set_focus()
        self.focused_widget = widget

    def cycle_focus(self, direction):
        if self.is_focused_widget_set():
            index = self.parameter_input_widgets.index(self.focused_widget)
            new_index = (index + direction) % len(self.parameter_input_widgets)
        else:
            new_index = 0

        self.focus_widget(self.parameter_input_widgets[new_index])

    def is_focused_widget_set(self):
        return self.focused_widget is not None

    # Event Handlers
    def on_draw(self):
        self.clear()
        self.static_batch.draw()
        self.fps_display.draw()
        self.simulation_batch.draw()

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
                self.record_table.on_mouse_motion(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.record_table.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for button_widget in self.button_widgets:
                if button_widget.is_mouseover(x, y):
                    button_widget.on_click()
                    break

            selected_data = self.record_table.on_mouse_press(x, y)
            if selected_data:
                self.load_plot(selected_data)

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
        if self.is_focused_widget_set():
            current_text = self.focused_widget.document.text
            if self.focused_widget is self.parameter_input_widgets[10]:
                if re.match(r'[\r\n]|^ |^.{38,}$', current_text + text):
                    return
            else:
                if not re.match(r'^(?!.{10,})[0-9]*\.?[0-9]*$', current_text + text):
                    return

            self.focused_widget.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.is_focused_widget_set():
            self.focused_widget.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.is_focused_widget_set():
            self.focused_widget.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            direction = -1 if (modifiers & pyglet.window.key.MOD_SHIFT) else 1
            self.cycle_focus(direction)

        elif symbol == pyglet.window.key.ENTER:
            if self.is_focused_widget_set():
                if self.focused_widget is self.parameter_input_widgets[0]:
                    self.update_fuel_flow_rate(float(self.focused_widget.document.text))
                elif self.focused_widget is self.parameter_input_widgets[1]:
                    self.update_engine_load(float(self.focused_widget.document.text))

                self.cycle_focus(1)

    # Simulation Control
    def update_simulation(self, dt):
        if not self.simulation_paused and not self.engine_stalled:
            scaled_dt = dt * self.simulation_speed_factor

            if self.simulation.crank.starter_motor_on or self.simulation.gas_simulation.decompression_valve_open:
                if self.simulation.crank.get_rpm() > self.simulation.gas_simulation.STARTING_RPM:
                    self.simulation.gas_simulation.decompression_valve_open = False
                else:
                    self.simulation.gas_simulation.decompression_valve_open = True

            self.simulation.update_all(scaled_dt)
            self.renderer.render(self.simulation.crank, self.simulation.connecting_rod, self.simulation.piston)
            
            if self.simulation.crank.angular_velocity < 0:
                print("Engine stalled")
                self.simulation.crank.angular_velocity = 0
                self.engine_stalled = True
                self.toggle_simulation_pause_button()
            elif self.simulation.crank.angular_velocity > 1047 and self.simulation.gas_simulation.moles_after_combustion > 0:
                print("Engine overspeed | Fuel cutout triggered.")
                self.update_fuel_flow_rate(0.0)

    def sample_graph_point(self, _dt):
        if self.simulation_paused is True:
            return
        current_time = (time.perf_counter() - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
        torque = round(self.simulation.crank.current_torque, 6)
        rpm = round(self.simulation.crank.get_rpm(), 6)
        self.renderer.store_graph_point(current_time, torque, rpm)

    def start_simulation(self, simulation_parameters, origin):
        for i, input in enumerate(simulation_parameters):
            self.parameter_input_widgets[i+2].set_current_value(input)
            self.parameter_input_widgets[i+2].document.text = ""

        self.parameter_input_widgets[0].set_current_value(0.0)
        self.parameter_input_widgets[1].set_current_value(0.0)
        self.parameter_input_widgets[0].document.text = ""
        self.parameter_input_widgets[1].document.text = ""

        self.renderer.close_plot(0)
        self.renderer_parameters = simulation_parameters.copy()
        self.simulation_batch = pyglet.graphics.Batch()
        # [0]=crank_radius, [2]=rod_length, [4]=piston_radius, [5]=piston_length, [7]=deck_clearance
        for i in [0, 2, 4, 5, 7]:
            simulation_parameters[i] = self.mm_to_m(simulation_parameters[i])

        self.simulation = Simulation(*simulation_parameters)
        self.renderer = Renderer(self.simulation_batch, origin, simulation_parameters[0], simulation_parameters[2], 
                                 simulation_parameters[4], simulation_parameters[5])
        self.start_time = time.perf_counter()
        self.elapsed_pause_time = 0
        self.button_widgets[3].label.text = "Save Configuration"
        self.simulation_paused = False
        self.engine_stalled = True

    # Buttons and User Input Handling
    def set_parameters_button(self):
        inputs = [widget.document.text for widget in self.parameter_input_widgets[2:10]]
        if "" in inputs:
            print("Error: All parameter fields must be filled in")
            return
        
        parameters = list(map(float, inputs))
        param_names = ['crank_radius', 'crank_mass', 'rod_length', 'rod_mass',
                       'piston_radius', 'piston_length', 'piston_mass', 'deck_clearance']

        for value, name in zip(parameters, param_names):
            if not self.validate_parameter(name, value):
                return

        if parameters[2] <= parameters[0]:
            print("Error: Connecting Rod Length cannot be smaller than Crank Radius")
            return

        self.start_simulation(parameters, self.origin)

    def toggle_simulation_pause_button(self):
        if hasattr(self, 'simulation'):
            self.simulation_paused = not self.simulation_paused
            if self.simulation_paused:
                print("Simulation paused")
                self.time_paused = time.perf_counter()
                current_time = (self.time_paused - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
                self.renderer.store_paused_point(current_time)
                named_parameters = ["Active Configuration"] + self.renderer_parameters
                self.renderer.plot_active_configuration_performance(named_parameters)
            else:
                print("Simulation resumed")
                time_resumed = time.perf_counter()
                self.elapsed_pause_time += time_resumed - self.time_paused
                self.renderer.close_plot(0)

    def ignition_starter_button(self):
        if hasattr(self, 'simulation') and self.simulation_paused is False:
            if self.engine_stalled:
                print("Starter motor activated")
                self.engine_stalled = False
                self.simulation.toggle_starter_motor()
                pyglet.clock.schedule_once(self.starter_cutout, 3)

    def starter_cutout(self, _dt):
        self.simulation.toggle_starter_motor()

    def update_fuel_flow_rate(self, fuel_flow_rate):
        if hasattr(self, 'simulation') and fuel_flow_rate != "":
            if not self.validate_parameter('fuel_flow', fuel_flow_rate):
                return
            self.simulation.update_fuel_flow_rate(fuel_flow_rate)
            current_time = (time.perf_counter() - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
            self.renderer.store_throttle_change_point(current_time, fuel_flow_rate)
            self.parameter_input_widgets[0].set_current_value(fuel_flow_rate)
            self.parameter_input_widgets[0].document.text = ""

    def update_engine_load(self, engine_load):
        if hasattr(self, 'simulation') and engine_load != "":
            self.simulation.update_engine_load(engine_load)
            current_time = (time.perf_counter() - self.start_time - self.elapsed_pause_time) * self.simulation_speed_factor
            self.renderer.store_engine_load_change_point(current_time, engine_load)
            self.parameter_input_widgets[1].set_current_value(engine_load)
            self.parameter_input_widgets[1].document.text = ""

    def save_config_button(self):
        if hasattr(self, 'renderer_parameters'):
            configuration_name = self.parameter_input_widgets[10].document.text
            conn = None
            if configuration_name != "":
                try:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    if self.button_widgets[3].label.text == "Overwrite Last Save":
                        self.delete_record(cursor, self.last_save_id)
    
                    self.save_configuration(cursor, configuration_name, *self.renderer_parameters)
                    self.last_save_id = cursor.lastrowid
                    self.save_engine_performance_data(cursor, self.last_save_id)
                    self.save_paused_points(cursor, self.last_save_id)
                    self.save_throttle_change_points(cursor, self.last_save_id)
                    self.save_engine_load_change_points(cursor, self.last_save_id)
                    conn.commit()

                    self.record_table.insert_rows(self.get_engine_design_entries())
                    self.parameter_input_widgets[10].document.text = ""
                    self.button_widgets[3].label.text = "Overwrite Last Save"
                except Exception as e:                    
                    print(f"Database error saving configuration: {str(e)}")
                    if conn:
                        conn.rollback()
                finally:
                    if conn:
                        conn.close()

    def load_config_button(self):
        data = self.record_table.get_focused_data()
        if data is not None:
            parameters = list(data)
            self.start_simulation(parameters[2:], self.origin)

    def delete_record_button(self):
        focused_row = self.record_table.get_focused_data()
        conn = None
        if focused_row is not None:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                focused_row_id = focused_row[0]
                if focused_row_id == self.last_save_id:
                    self.button_widgets[3].label.text = "Save Configuration"
                self.renderer.close_plot(focused_row_id)
                self.delete_record(cursor, focused_row_id)
                conn.commit()

                self.record_table.insert_rows(self.get_engine_design_entries())
            except Exception as e:
                print(f"Error deleting record: {str(e)}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()

    # Database Functions
    def delete_record(self, cursor, save_id):
        cursor.execute('DELETE FROM engine_designs WHERE id = ?', (save_id,))
        cursor.execute('DELETE FROM engine_performance_data WHERE engine_design_id = ?', (save_id,))
        cursor.execute('DELETE FROM paused_points WHERE engine_design_id = ?', (save_id,))
        cursor.execute('DELETE FROM throttle_change_points WHERE engine_design_id = ?', (save_id,))
        cursor.execute('DELETE FROM engine_load_change_points WHERE engine_design_id = ?', (save_id,))

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

    def save_engine_load_change_points(self, cursor, engine_design_id):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engine_load_change_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine_design_id INTEGER,
                time REAL,
                engine_load REAL,
                FOREIGN KEY(engine_design_id) REFERENCES engine_designs(id)
            )
        ''')
        for time_point, engine_load in self.renderer.engine_load_change_points:
            cursor.execute('''
                INSERT INTO engine_load_change_points (engine_design_id, time, engine_load)
                VALUES (?, ?, ?)
            ''', (engine_design_id, time_point, engine_load))

    def get_engine_design_entries(self):
        conn = None
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_designs'")
            if cursor.fetchone() is not None:
                cursor.execute('SELECT * FROM engine_designs')
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
            if conn:
                conn.close()

            return entries
        
    def load_plot(self, selected_record):
        engine_design_id = selected_record[0]
        conn = None
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            data_points, paused_points, throttle_changes, load_changes = self.load_engine_performance_data(cursor, engine_design_id)
            if data_points:
                time_points, torque_points, rpm_points = zip(*data_points)
            else:
                time_points, torque_points, rpm_points = [], [], []
        except Exception as e:
            print(f"Database error in loading plot: {str(e)}")
            time_points, torque_points, rpm_points = [], [], []
            paused_points = []
            throttle_changes = []
            load_changes = []
        finally:
            if conn:
                conn.close()

            self.renderer.plot_engine_performance_graph(time_points, torque_points, rpm_points, paused_points,
                                       throttle_changes, load_changes, selected_record[1:], engine_design_id)
        
    def load_engine_performance_data(self, cursor, engine_design_id):
        cursor.execute('''
            SELECT time, torque, rpm FROM engine_performance_data
            WHERE engine_design_id = ?
            ORDER BY time ASC
        ''', (engine_design_id,))
        data_points = cursor.fetchall()
        
        cursor.execute('''
            SELECT 'pause_point' as type, paused_time as time, NULL as value
            FROM paused_points 
            WHERE engine_design_id = ?
            UNION ALL
            SELECT 'throttle_change_point', time, fuel_flow_rate
            FROM throttle_change_points
            WHERE engine_design_id = ?
            UNION ALL
            SELECT 'load_change_point', time, engine_load
            FROM engine_load_change_points
            WHERE engine_design_id = ?
        ''', (engine_design_id, engine_design_id, engine_design_id))
        event_points = cursor.fetchall()
        
        paused_points = []
        throttle_change_points = []
        load_change_points = []

        for type, time, value in event_points:
            if type == 'pause_point':
                paused_points.append(time)
            elif type == 'throttle_change_point':
                throttle_change_points.append((time, value))
            else:
                load_change_points.append((time, value))
                
        return data_points, paused_points, throttle_change_points, load_change_points

    # Utility Functions
    def mm_to_m(self, value):
        return value / 1000.0

    def validate_parameter(self, param_name, value):
        constraints = self.PARAMETER_CONSTRAINTS[param_name]
        if value < constraints['min']:
            print(f"Error: {constraints['name']} too small (minimum: {constraints['min']})")
            return False
        if value > constraints['max']:
            print(f"Error: {constraints['name']} too large (maximum: {constraints['max']})")
            return False
        return True

if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    simulation = SimulationWindow(width=1050, height=900, resizable=False, caption="Piston Engine Simulation", vsync=False)
    pyglet.clock.schedule_interval(simulation.update_simulation, 1/3000) 
    pyglet.clock.schedule_interval(simulation.sample_graph_point, 1/1000)
    pyglet.app.run(interval=1/60)
