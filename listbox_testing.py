import pyglet
from pyglet.window import mouse
import sqlite3
import time

def get_database_entries():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Time, IntegerValue, StringValue FROM engines')
    entries = cursor.fetchall()
    conn.close()
    return [f"{row[2]} (Value: {row[1]}, Time: {row[0]:.2f})" for row in entries]

def create_test_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engines (
            Time REAL,
            IntegerValue INTEGER,
            StringValue TEXT
        )
    ''')
    cursor.execute('DELETE FROM engines')
    
    test_data = [
        (time.time(), 42, "Fast Engine"),
        (time.time(), 99, "Power Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 127, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 126, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 123, "Eco Engine"),
        (time.time(), 124, "Eco Engine"),
    ]
    cursor.executemany(
        'INSERT INTO engines (Time, IntegerValue, StringValue) VALUES (?, ?, ?)',
        test_data
    )
    conn.commit()
    conn.close()
class ListRow:
    def __init__(self, text, x, y, width, height, batch):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        
        label_x = x + width // 2
        label_y = y + height // 2
        self.label = pyglet.text.Label(
            text,
            x=label_x, y=label_y,
            anchor_x='center', anchor_y='center',
            color=(0, 0, 0, 255),
            batch=batch
        )
        self.bounding_box = pyglet.shapes.Rectangle(
            x, y, width, height,
            color=(200, 200, 220),  # Default color matching main.py buttons
            batch=batch
        )

    def is_mouseover(self, mx, my):
        return (self.bounding_box.x <= mx <= self.bounding_box.x + self.bounding_box.width and
                self.bounding_box.y <= my <= self.bounding_box.y + self.bounding_box.height)
    
    def set_hover(self, is_hover):
        if is_hover:
            self.bounding_box.color = (150, 150, 170)  # Hover color matching main.py buttons
        else:
            self.bounding_box.color = (200, 200, 220)  # Default color

class ListBox:
    """
    A scrolling list box styled in a way consistent with main.py's approach to UI elements.
    Double-click selects an item, hovering changes background color, supports scrolling.
    """
    def __init__(self, items, x, y, width, height, batch):
        self.items_data = items
        self.rows = []
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        self.scroll_offset = 0
        self.item_height = 30  # matches main.py's style of bigger UI elements
        self.visible_count = self.height // self.item_height
        self.selected_index = None
        self.last_click_time = 0
        self.last_click_index = None
        
        self.load_rows()  # create row objects for each item
        self.update_row_positions()
    
    def load_rows(self):
        self.rows.clear()
        for text in self.items_data:
            # temporary y=0, will position them properly in update_row_positions
            self.rows.append(ListRow(text, self.x, 0, self.width, self.item_height, self.batch))

    def update_row_positions(self):
        """
        Position rows based on scroll_offset and visible_count.
        """
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_count, len(self.rows))
        
        current_y = self.y + self.height
        # Hide/Show rows as needed
        for i, row in enumerate(self.rows):
            if i < start_idx or i >= end_idx:
                # place offscreen so it won't show
                row.bounding_box.x = -9999
                row.bounding_box.y = -9999
                row.label.x = -9999
                row.label.y = -9999
                continue
            # row i is visible
            row_y = current_y - self.item_height
            row.bounding_box.x = self.x
            row.bounding_box.y = row_y
            row.bounding_box.width = self.width
            row.bounding_box.height = self.item_height

            row.label.x = self.x + self.width // 2
            row.label.y = row_y + self.item_height // 2
            
            current_y -= self.item_height

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height):
            return
        max_offset = max(0, len(self.rows) - self.visible_count)
        self.scroll_offset = min(max(0, self.scroll_offset - int(scroll_y)), max_offset)
        self.update_row_positions()

    def find_row_at_position(self, mx, my):
        """
        Returns index of the row if found, else None
        """
        for i, row in enumerate(self.rows):
            if row.is_mouseover(mx, my):
                return i
        return None

    def on_mouse_motion(self, mx, my, _dx, _dy):
        for row in self.rows:
            row.set_hover(False)
            
        # Only check visible rows
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_count, len(self.rows))
        
        # Update hover state for the row under cursor
        for i in range(start_idx, end_idx):
            if self.rows[i].is_mouseover(mx, my):
                self.rows[i].set_hover(True)
                break

    def on_mouse_press(self, mx, my, button, modifiers):
        if button == mouse.LEFT:
            clicked_idx = self.find_row_at_position(mx, my)
            if clicked_idx is not None:
                current_time = time.time()
                # Double-click check
                if (clicked_idx == self.last_click_index and
                    current_time - self.last_click_time < 0.5):
                    self.selected_index = clicked_idx
                    return self.rows[clicked_idx].text
                self.last_click_time = current_time
                self.last_click_index = clicked_idx
        return None

class SimulationWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(800, 600, "Engine Selection")
        self.batch = pyglet.graphics.Batch()
        database_entries = get_database_entries()
        
        self.list_box = ListBox(database_entries, x=50, y=50, width=400, height=300, batch=self.batch)
    
    def on_draw(self):
        self.clear()
        self.batch.draw()
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.list_box.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.list_box.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, button, modifiers):
        selected = self.list_box.on_mouse_press(x, y, button, modifiers)
        if selected:
            print(f"Selected: {selected}")

if __name__ == "__main__":
    create_test_database()
    window = SimulationWindow()
    pyglet.app.run()