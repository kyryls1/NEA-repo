import pytest
import sqlite3
import pyglet
import time
import math
from main import SimulationWindow

def mock_database_error(self, engine_design_id):
    raise sqlite3.Error("Mock database error")

def mock_unexpected_error(*args):
    raise Exception("Unexpected error")

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

# Test behaviour of record table on single, double, triple click.
def test_listrow_mouse_click_behaviour(setup_test_database):
    cursor = setup_test_database.cursor()
    cursor.execute("INSERT INTO engine_designs VALUES (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("Test Config", 20, 5, 70, 2, 30, 50, 1, 3))
    setup_test_database.commit()

    test_window = SimulationWindow(visible=False)

    table_row = test_window.record_table.rows[0]
    x = table_row.bounding_box.x + 10
    y = table_row.bounding_box.y + 10

    # Single click: row focused, function not triggered.
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == table_row
    assert test_window.renderer.open_design_plots == {}

    # Double click: function triggered, row focus cleared.
    time.sleep(1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == None
    assert len(test_window.renderer.open_design_plots) == 1

    # Triple click: function trigerred once, row focus set.
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    assert test_window.record_table.focused_row == table_row
    assert len(test_window.renderer.open_design_plots) == 1

# Test exception handling when loading plot.
def test_load_plot_error(setup_test_database, capsys):
    cursor = setup_test_database.cursor()
    cursor.execute("INSERT INTO engine_designs VALUES (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("Test Config", 20, 5, 70, 2, 30, 50, 1, 3))
    setup_test_database.commit()

    test_window = SimulationWindow(visible=False)

    # Drop table to force error
    cursor.execute("DROP TABLE engine_performance_data")
    setup_test_database.commit()

    # Double click on record
    table_row = test_window.record_table.rows[0]
    x = table_row.bounding_box.x + 10
    y = table_row.bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    time.sleep(0.1)
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    captured = capsys.readouterr()
    assert "Database error in loading plot" in captured.out

# Test set parameters button behaviour.
def test_set_parameters_button(setup_test_database):
    test_window = SimulationWindow(visible=False)

    parameters = {2: "20", 3: "5", 4: "70", 5: "2", 6: "30", 7: "50", 8: "3", 9: "1"}
    
    # Enter valid parameters
    for i, value in parameters.items():
        test_window.parameter_input_widgets[i].document.text = value

    assert test_window.simulation_paused is True
    
    # Click Set Parameters button
    x = test_window.button_widgets[1].bounding_box.x + 10
    y = test_window.button_widgets[1].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    assert test_window.simulation_paused is False
    assert test_window.simulation.crank.radius == 0.02
    assert test_window.simulation.crank.mass == 5
    assert math.isclose(test_window.simulation.connecting_rod.length_squared, 0.0049, abs_tol=1e-15)
    assert test_window.simulation.connecting_rod.mass == 2
    assert test_window.simulation.piston.radius == 0.03
    assert test_window.simulation.piston.length == 0.05
    assert test_window.simulation.piston.mass == 3

# Test save configuration button behaviour.
def test_save_config_button(setup_test_database):
    test_window = SimulationWindow(visible=False)
    
    #Enter valid parameters
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
    
    assert len(saved_records) == 1
    assert "Test Save" in saved_records[0][1]
    assert test_window.button_widgets[3].label.text == "Overwrite Last Save"
    assert test_window.parameter_input_widgets[10].document.text == ""
    assert len(test_window.record_table.rows) == 1

# Test delete configuration button behaviour.
def test_delete_record_button(setup_test_database):
    # Save a record
    test_window = SimulationWindow(visible=False)
    parameters = {2: "20", 3: "5", 4: "70", 5: "2", 6: "30", 7: "50", 8: "3", 9: "1"}
    for i, value in parameters.items():
        test_window.parameter_input_widgets[i].document.text = value
    x = test_window.button_widgets[1].bounding_box.x + 10
    y = test_window.button_widgets[1].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    test_window.parameter_input_widgets[10].document.text = "Test Save"
    x = test_window.button_widgets[3].bounding_box.x + 10
    y = test_window.button_widgets[3].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)

    # Click on the record
    table_row = test_window.record_table.rows[0]
    x = table_row.bounding_box.x + 10
    y = table_row.bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    # Click Delete Record button
    x = test_window.button_widgets[5].bounding_box.x + 10
    y = test_window.button_widgets[5].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    
    # Verify record was deleted
    cursor = setup_test_database.cursor()
    cursor.execute("SELECT * FROM engine_designs")
    assert len(cursor.fetchall()) == 0
    assert len(test_window.record_table.rows) == 0

# Test exception handling when deleting record.
def test_delete_record_button_error(setup_test_database, capsys):
    # Save a record
    test_window = SimulationWindow(visible=False)
    parameters = {2: "20", 3: "5", 4: "70", 5: "2", 6: "30", 7: "50", 8: "3", 9: "1"}
    for i, value in parameters.items():
        test_window.parameter_input_widgets[i].document.text = value
    x = test_window.button_widgets[1].bounding_box.x + 10
    y = test_window.button_widgets[1].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)
    test_window.parameter_input_widgets[10].document.text = "Test Save"
    x = test_window.button_widgets[3].bounding_box.x + 10
    y = test_window.button_widgets[3].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)

    # Click on the record
    table_row = test_window.record_table.rows[0]
    x = table_row.bounding_box.x + 10
    y = table_row.bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)

    # Create mock database error
    test_window.delete_record = mock_database_error

    # Click Delete Record button
    x = test_window.button_widgets[5].bounding_box.x + 10
    y = test_window.button_widgets[5].bounding_box.y + 10
    test_window.on_mouse_press(x, y, pyglet.window.mouse.LEFT, None)

    # Verify error output and record not deleted
    captured = capsys.readouterr()
    assert "Mock database error" in captured.out
    cursor = setup_test_database.cursor()
    cursor.execute("SELECT * FROM engine_designs")
    assert len(cursor.fetchall()) == 1

# Test response to database error when retrieving records.
def test_get_engine_design_entries_db_error(setup_test_database, capsys):
    cursor = setup_test_database.cursor()
    cursor.execute("DROP TABLE engine_designs")
    setup_test_database.commit()

    _ = SimulationWindow(visible=False)
    
    captured = capsys.readouterr()
    assert "Database error" in captured.out

# Test response to unexpected error when retrieving records.
def test_get_engine_design_entries_unexpected_error(setup_test_database, capsys, monkeypatch):
    monkeypatch.setattr(sqlite3, 'connect', mock_unexpected_error)
    _ = SimulationWindow(visible=False)
    
    captured = capsys.readouterr()
    assert "Unexpected error" in captured.out
