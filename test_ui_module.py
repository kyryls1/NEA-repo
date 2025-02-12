import pytest
import sqlite3
import pyglet
import time
from main import SimulationWindow

@pytest.fixture
def setup_test_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engine_performance_data (
            id INTEGER PRIMARY KEY,
            engine_design_id INTEGER,
            torque REAL,
            rpm REAL,
            time REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paused_points (
            id INTEGER PRIMARY KEY,
            engine_design_id INTEGER,
            paused_time REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS throttle_change_points (
            id INTEGER PRIMARY KEY,
            engine_design_id INTEGER,
            time REAL,
            fuel_flow_rate REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engine_load_change_points (
            id INTEGER PRIMARY KEY,
            engine_design_id INTEGER,
            time REAL,
            engine_load REAL
        )
    ''')
    conn.commit()

    yield conn

    cursor.execute('DROP TABLE IF EXISTS engine_designs')
    cursor.execute('DROP TABLE IF EXISTS engine_performance_data')
    cursor.execute('DROP TABLE IF EXISTS paused_points')
    cursor.execute('DROP TABLE IF EXISTS throttle_change_points')
    cursor.execute('DROP TABLE IF EXISTS engine_load_change_points')
    conn.commit()
    conn.close()

def test_listrow_mouse_click_behaviour(setup_test_database):
    """Test 1: Single click on saves table record should yield no response."""
    cursor = setup_test_database.cursor()
    cursor.execute("INSERT INTO engine_designs VALUES (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("Test Config", 20, 5, 70, 2, 30, 50, 1, 3))

    # Insert 5 more rows (total 8 rows) so that one row is outside the visible bounds
    setup_test_database.commit()

    test_window = SimulationWindow(visible=False)

    table_row = test_window.record_table.rows[0]
    x = table_row.bounding_box.x + 10
    y = table_row.bounding_box.y + 10

    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == table_row
    assert test_window.renderer.open_design_plots == {}

    time.sleep(1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == None
    assert len(test_window.renderer.open_design_plots) == 1

    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == table_row
    assert len(test_window.renderer.open_design_plots) == 1

def test_set_parameters_button(setup_test_database):
    """Test that setting valid parameters starts the simulation."""
    test_window = SimulationWindow(visible=False)
    
    parameters = {2: "20", 3: "5", 4: "70", 5: "2", 6: "30", 7: "50", 8: "3", 9: "1"}
    
    for i, value in parameters.items():
        test_window.parameter_input_widgets[i].document.text = value

    assert test_window.simulation_paused is True
    
    x = test_window.button_widgets[1].bounding_box.x + 10
    y = test_window.button_widgets[1].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    assert test_window.simulation_paused is False
    assert hasattr(test_window, 'simulation')

def test_save_config_button(setup_test_database):
    """Test saving a new configuration."""
    test_window = SimulationWindow(visible=False)
    
    # First set valid parameters and start simulation
    parameters = {2: "20", 3: "5", 4: "70", 5: "2", 6: "30", 7: "50", 8: "3", 9: "1"}
    for i, value in parameters.items():
        test_window.parameter_input_widgets[i].document.text = value
    
    # Click Set Parameters button
    x = test_window.button_widgets[1].bounding_box.x + 10
    y = test_window.button_widgets[1].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    # Enter configuration name
    test_window.parameter_input_widgets[10].document.text = "Test Save"
    
    # Click Save Configuration button
    x = test_window.button_widgets[3].bounding_box.x + 10
    y = test_window.button_widgets[3].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    # Verify save was successful
    cursor = setup_test_database.cursor()
    cursor.execute("SELECT * FROM engine_designs")
    saved_records = cursor.fetchall()
    
    assert len(saved_records) == 1, "One record should be saved"
    assert "Test Save" in saved_records[0][1], "Configuration name should be saved"
    assert test_window.button_widgets[3].label.text == "Overwrite Last Save"
    assert test_window.parameter_input_widgets[10].document.text == ""
    assert len(test_window.record_table.rows) == 1

