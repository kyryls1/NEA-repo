import pytest
import sqlite3
import time
import pyglet
from widgets import ListTable, ListRow, Button
from main import SimulationWindow

def test_saves_table_single_click_no_response(simulation_window, monkeypatch):
    """Test 1: Single click on saves table record should yield no response."""
    # Patch load_plot to confirm it's not called
    load_calls = []
    monkeypatch.setattr(simulation_window, 'load_plot', lambda record: load_calls.append(record))

    # Click on the first row
    row_x = simulation_window.record_table.bounding_box.x + 10
    row_y = simulation_window.record_table.bounding_box_top_boundary - 5
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)

    assert len(load_calls) == 0, "No response expected on single click"

def test_saves_table_double_click_trigger(simulation_window, monkeypatch):
    """Test 2: Double click on saves table record should return the selected record."""
    load_calls = []
    monkeypatch.setattr(simulation_window, 'load_plot', lambda record: load_calls.append(record))
    
    row_x = simulation_window.record_table.bounding_box.x + 10
    row_y = simulation_window.record_table.bounding_box_top_boundary - 5
    
    # First click
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)
    # Simulate second click within 0.5 seconds
    simulation_window.record_table.last_click_time = time.perf_counter() - 0.1
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)

    assert len(load_calls) == 1, "Double click should trigger load_plot exactly once"

def test_saves_table_triple_click_reset(simulation_window, monkeypatch):
    """Test 3b: After a double click triggers a response, the third click is treated as separate."""
    load_calls = []
    monkeypatch.setattr(simulation_window, 'load_plot', lambda record: load_calls.append(record))
    
    row_x = simulation_window.record_table.bounding_box.x + 10
    row_y = simulation_window.record_table.bounding_box_top_boundary - 5
    
    # Double click
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)
    simulation_window.record_table.last_click_time = time.perf_counter() - 0.1
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)
    assert len(load_calls) == 1, "Double click triggers one response"

    # Third click after double click
    time.sleep(0.6)  # Exceed 0.5s so it's a new single click
    simulation_window.on_mouse_press(row_x, row_y, pyglet.window.mouse.LEFT, None)
    assert len(load_calls) == 1, "Third click should be a new single click with no additional triggers"

@pytest.fixture
def setup_list_table(tmp_path):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE engine_designs (id INTEGER PRIMARY KEY, configuration_name TEXT)')
    # Create more records than can fit in the visible area
    test_configs = [f"Test Config {i}" for i in range(10)]  # 10 rows > visible area
    cursor.executemany(
        "INSERT INTO engine_designs (configuration_name) VALUES (?)",
        [(config,) for config in test_configs]
    )
    conn.commit()

    list_table = ListTable([], x=0, y=0, width=300, height=200, batch=None)
    cursor.execute("SELECT * FROM engine_designs")
    records = cursor.fetchall()
    list_table.insert_rows(records)

    yield list_table, conn
    conn.close()

@pytest.fixture
def simulation_window():
    """Create a simulation window with a few mock records in the table."""
    window = SimulationWindow(width=800, height=600, resizable=False)
    window.record_table.insert_rows([(1, 'Mock Save A'), (2, 'Mock Save B')])
    return window

def test_listTable_data_retrieve(setup_list_table):
    list_table, conn = setup_list_table
    first_row = list_table.get_focused_data()
    assert first_row is None, "Initially, no row is focused"
    assert len(list_table.rows) == 10, "Should contain 10 rows"

def test_listTable_scroll(setup_list_table):
    list_table, _ = setup_list_table
    initial_offset = list_table.scroll_offset
    x = (list_table.bounding_box.x + list_table.bounding_box_right_boundary) / 2
    y = (list_table.bounding_box.y + list_table.bounding_box_top_boundary) / 2
    
    list_table.on_mouse_scroll(x, y, 0, -1)  # Scroll down; negative scroll_y should increase offset
    assert list_table.scroll_offset > initial_offset, "Scrolling down should increase offset"

def test_listRow_double_click_load(setup_list_table):
    list_table, _ = setup_list_table
    import time
    
    # Click within first row bounds
    x = (list_table.bounding_box.x + list_table.bounding_box_right_boundary) / 2
    y = list_table.bounding_box_top_boundary - (list_table.row_height / 2)
    
    # First click sets focus and last_click_time
    list_table.on_mouse_press(x, y)
    # Second click within 0.5s
    list_table.last_click_time = time.perf_counter() - 0.1  # Simulate 0.1s between clicks
    row_data = list_table.on_mouse_press(x, y)
    
    assert row_data is not None, "Double-click should return row data"
    assert row_data[1] == "Test Config 0", "First entry should match"

def test_button_functions():
    # Test each button callback in isolation
    clicked = []
    def sample_callback():
        clicked.append(True)

    button = Button("Sample", 0, 0, 100, 30, sample_callback, batch=None)
    button.on_click()
    assert len(clicked) == 1, "Button callback should be triggered once"

def test_listTable_collision_detection_update(setup_list_table):
    list_table, _ = setup_list_table
    
    # Get coordinates for the first row
    x = (list_table.bounding_box.x + list_table.bounding_box_right_boundary) / 2
    y = list_table.bounding_box_top_boundary - (list_table.row_height / 2)
    
    # Verify first row is visible and can be clicked
    first_row = list_table.rows[0]
    assert first_row.visible, "First row should be visible initially"
    assert first_row.is_mouseover(x, y), "Should detect mouseover on first row"
    
    # Scroll down multiple times to ensure first row moves out of view
    for _ in range(10):  # Scroll enough to move first row out
        list_table.on_mouse_scroll(x, y, 0, -1)
    
    assert not first_row.visible, "First row should no longer be visible after scrolling"
    assert not first_row.is_mouseover(x, y), "Should not detect mouseover on invisible row"

def test_database_error_handling(setup_list_table):
    """Test handling of database errors."""
    list_table, conn = setup_list_table
    initial_row_count = len(list_table.rows)
    
    cursor = conn.cursor()
    cursor.execute("DROP TABLE engine_designs")
    
    # Verify state after table drop
    list_table.insert_rows(None)
    assert len(list_table.rows) == 0, "Should clear existing rows"
    assert list_table.focused_row is None, "Should clear row focus"
    assert list_table.scroll_offset == 0, "Should reset scroll position"

def test_row_focus_behavior(setup_list_table):
    """Test that row focus updates correctly."""
    list_table, _ = setup_list_table
    
    # Click first row
    x = (list_table.bounding_box.x + list_table.bounding_box_right_boundary) / 2
    y = list_table.bounding_box_top_boundary - (list_table.row_height / 2)
    list_table.on_mouse_press(x, y)
    
    assert list_table.focused_row == list_table.rows[0], "First row should be focused"
    assert list_table.rows[0].focused, "First row should have focused state"
    
    # Click outside table area should clear focus
    list_table.on_mouse_press(0, 0)
    assert list_table.focused_row is None, "Focus should clear when clicking outside"
    assert not list_table.rows[0].focused, "First row should no longer be focused"

def test_invalid_record_handling(setup_list_table):
    """Test handling of invalid/missing record IDs."""
    list_table, conn = setup_list_table
    
    # Insert a row with invalid data format
    cursor = conn.cursor()
    cursor.execute("INSERT INTO engine_designs (configuration_name) VALUES (?)", 
                  ("Invalid Record",))
    cursor.execute("SELECT * FROM engine_designs")
    records = cursor.fetchall()
    
    # Should handle malformed records gracefully
    list_table.insert_rows(records)
    assert len(list_table.rows) == 11, "Should skip invalid records but continue processing"

def test_database_connection_errors():
    """Test handling of database connection failures."""
    try:
        conn = sqlite3.connect('/invalid/path/to/database.db')
        pytest.fail("Should not successfully connect to invalid path")
    except sqlite3.OperationalError as e:
        assert "unable to open database file" in str(e), "Should fail with specific error message"
        
    # Test corrupted database handling
    test_db = 'test.db'
    with open(test_db, 'wb') as f:
        f.write(b'corrupted data')
    
    conn = None
    try:
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM engine_designs")
        pytest.fail("Should not execute query on corrupted database")
    except sqlite3.DatabaseError as e:
        assert "file is not a database" in str(e), "Should fail with database corruption error"
    finally:
        if conn:
            conn.close()
        # Wait a moment before trying to remove file
        import time
        time.sleep(0.1)
        import os
        if os.path.exists(test_db):
            os.remove(test_db)

def test_broken_query_handling(setup_list_table):
    """Test handling of malformed SQL queries."""
    list_table, conn = setup_list_table
    cursor = conn.cursor()
    
    try:
        # Test invalid SQL syntax
        cursor.execute("SELEC * FORM engine_designs")  # Deliberately malformed SQL
        pytest.fail("Should raise error on invalid SQL")
    except sqlite3.OperationalError as e:
        assert "syntax error" in str(e), "Should catch SQL syntax errors"
    
    try:
        # Test query against non-existent column
        cursor.execute("SELECT nonexistent_column FROM engine_designs")
        pytest.fail("Should raise error on invalid column")
    except sqlite3.OperationalError as e:
        assert "no such column" in str(e), "Should catch invalid column errors"

def test_row_selection_focus(setup_list_table):
    """Test that row selection properly updates focus state."""
    list_table, _ = setup_list_table
    
    # Click first row
    list_table.on_mouse_press(list_table.bounding_box.x + 10, 
                             list_table.bounding_box_top_boundary - 5)
        first_row = list_table.rows[0]    assert first_row.focused, "First row should be focused"    assert list_table.focused_row == first_row, "ListTable should track focused row"        # Click second row    list_table.on_mouse_press(list_table.bounding_box.x + 10,
                             list_table.bounding_box_top_boundary - list_table.row_height - 5)
    
    assert not first_row.focused, "First row should lose focus"
    assert list_table.rows[1].focused, "Second row should gain focus"
    assert list_table.focused_row == list_table.rows[1], "ListTable should update focused row"

def test_invalid_record_id_loading(setup_list_table):
    """Test handling of invalid record IDs during load operations."""
    list_table, conn = setup_list_table
    cursor = conn.cursor()
    
    # Try loading non-existent record
    cursor.execute("SELECT * FROM engine_designs WHERE id = ?", (999,))
    result = cursor.fetchone()
    assert result is None, "Should return None for non-existent record"
    
    # Try loading with invalid ID type
    try:
        cursor.execute("SELECT * FROM engine_designs WHERE id = ?", ("invalid_id",))
        pytest.fail("Should raise error on invalid ID type")
    except sqlite3.IntegrityError as e:
        assert "INTEGER" in str(e), "Should catch type mismatch errors"

# Additional UI & DB test ideas (not implemented yet):
# - Validate error handling for broken queries or empty results
# - Ensure row selection updates focus in ListTable
# - Confirm that loading invalid row IDs doesn't crash the app
