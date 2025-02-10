import sqlite3
from main import SimulationWindow

def setup_test_database(conn, cursor):
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

def cleanup_test_database(conn, cursor):
    cursor.execute('DROP TABLE IF EXISTS engine_designs')
    cursor.execute('DROP TABLE IF EXISTS engine_performance_data')
    cursor.execute('DROP TABLE IF EXISTS paused_points')
    cursor.execute('DROP TABLE IF EXISTS throttle_change_points')
    cursor.execute('DROP TABLE IF EXISTS engine_load_change_points')
    conn.commit()

def test_delete_record(conn, cursor):
    print("-" * 50)
    print("Test delete_record with existing record...")

    cursor.execute('INSERT INTO engine_designs VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  ("Test Config", 30.0, 10.0, 80.0, 5.0, 35.0, 50.0, 2.0, 8.0))
    engine_design_id = cursor.lastrowid
    cursor.execute('INSERT INTO engine_performance_data VALUES (NULL, ?, ?, ?, ?)', (engine_design_id, 0.1, 50.0, 1000.0))
    cursor.execute('INSERT INTO paused_points VALUES (NULL, ?, ?)', (engine_design_id, 0.15))
    cursor.execute('INSERT INTO throttle_change_points VALUES (NULL, ?, ?, ?)', (engine_design_id, 0.2, 0.5))
    cursor.execute('INSERT INTO engine_load_change_points VALUES (NULL, ?, ?, ?)', (engine_design_id, 0.25, 100.0))

    cursor.execute('SELECT COUNT(*) FROM engine_designs')
    print(f"Number of records in engine_designs before delete_record called: {cursor.fetchone()[0]}")
    
    SimulationWindow.delete_record(None, cursor, engine_design_id)
    
    cursor.execute('SELECT COUNT(*) FROM engine_designs')
    count = cursor.fetchone()[0]
    assert count == 0
    print(f"Number of records in engine_designs after delete_record called: {count}")
    cursor.execute('SELECT COUNT(*) FROM engine_performance_data')
    assert cursor.fetchone()[0] == 0
    cursor.execute('SELECT COUNT(*) FROM paused_points')
    assert cursor.fetchone()[0] == 0
    cursor.execute('SELECT COUNT(*) FROM throttle_change_points')
    assert cursor.fetchone()[0] == 0
    cursor.execute('SELECT COUNT(*) FROM engine_load_change_points')
    assert cursor.fetchone()[0] == 0

    print("✓ Unit Test Passed: Record successfully deleted")
    conn.rollback()

def test_save_configuration(conn, cursor):
    print("-" * 50)
    print("Test save_configuration with existing engine_designs table...")

    test_params = [30.0, 10.0, 80.0, 5.0, 35.0, 50.0, 10.0, 1.0]
    SimulationWindow.save_configuration(None, cursor, "Test Config", *test_params)
    
    cursor.execute('SELECT * FROM engine_designs')
    row = cursor.fetchone()
    assert row is not None
    assert "| Test Config" in row[1], "Configuration name improperly formatted"
    print(f"Saved row: {row}")
    print("✓ Unit Test Passed: Configuration saved successfully")
    
    conn.rollback()

def test_save_configuration_with_missing_table(conn, cursor):
    print("-" * 50)
    print("Test save_configuration with no existing table...")

    cursor.execute('DROP TABLE IF EXISTS engine_designs')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_designs'")
    table_exists = cursor.fetchone() is not None
    assert table_exists is False
    print(f"'engine_designs' table in database before calling save_configuration: {table_exists}")
    
    test_params = [30.0, 10.0, 80.0, 5.0, 35.0, 50.0, 10.0, 1.0]
    SimulationWindow.save_configuration(None, cursor, "Test Config", *test_params)

    cursor.execute('SELECT COUNT(*) FROM engine_designs')
    count = cursor.fetchone()[0]
    assert count == 1
    print(f"Number of records in engine_designs after save_configuration called: {count}")

    cursor.execute('SELECT * FROM engine_designs')
    row = cursor.fetchone()
    assert row is not None
    print(f"Saved row: {row}")
    print("✓ Unit Test Passed: Table created and configuration saved successfully")
    
    conn.rollback()

def test_load_performance_data(conn, cursor):
    print("-" * 50)
    print("Test load_performance_data with valid data...")
    
    test_data = [(0.1, 50.0, 1000.0), (0.2, 55.0, 1100.0)]
    for time_val, torque, rpm in test_data:
        cursor.execute('INSERT INTO engine_performance_data VALUES (NULL, ?, ?, ?, ?)',
                       (1, torque, rpm, time_val))

    test_paused_points = [0.12, 0.22]
    for time in test_paused_points:
        cursor.execute('INSERT INTO paused_points VALUES (NULL, ?, ?)', (1, time))

    test_throttle_change_points = [(0.13, 0.7), (0.23, 0.9)]
    for time, value in test_throttle_change_points:
        cursor.execute('INSERT INTO throttle_change_points VALUES (NULL, ?, ?, ?)', (1, time, value))

    test_load_change_points = [(0.14, 120.0)]
    for time, value in test_load_change_points:
        cursor.execute('INSERT INTO engine_load_change_points VALUES (NULL, ?, ?, ?)', (1, time, value))
    
    print(f"Inserted {len(test_data)} engine_performance records, "
          f"{len(test_paused_points)} paused_points records, "
          f"{len(test_throttle_change_points)} throttle_change_points records, "
          f"and {len(test_load_change_points)} engine_load_change points records.")
    
    data_points, paused_points, throttle_change_points, load_change_points = SimulationWindow.load_engine_performance_data(None, cursor, 1)
    
    time_vals, torques, rpms = zip(*data_points)
    print(f"Loaded performance data: {data_points}")
    print(f"Time values: {time_vals}")
    print(f"Torque values: {torques}")
    print(f"RPM values: {rpms}")
    assert time_vals == (0.1, 0.2)
    assert torques == (50.0, 55.0)
    assert rpms == (1000.0, 1100.0)

    print(f"Paused points: {paused_points}")
    print(f"Throttle change points: {throttle_change_points}")
    print(f"Engine load change points: {load_change_points}")
    assert paused_points == test_paused_points
    assert throttle_change_points == test_throttle_change_points
    assert load_change_points == test_load_change_points
    
    print("✓ Unit Test Passed: Performance and event data loaded successfully")
    conn.rollback()

if __name__ == "__main__":
    print("Running main.py tests...")
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()
    cleanup_test_database(conn, cursor)
    setup_test_database(conn, cursor)
    
    test_delete_record(conn, cursor)
    test_save_configuration(conn, cursor)
    test_save_configuration_with_missing_table(conn, cursor)
    test_load_performance_data(conn, cursor)
    
    cleanup_test_database(conn, cursor)
    conn.close()
    print("All tests completed.")