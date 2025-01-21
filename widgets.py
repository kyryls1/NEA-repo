import pyglet
import time

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
    
    def set_hover(self, x, y):
        if self.is_mouseover(x, y):
            self.bounding_box.color = (150, 150, 170)
        else:
            self.bounding_box.color = (200, 200, 220)

    def on_click(self):
        self.callback()

class ListRow:
    def __init__(self, text, x, y, width, height, batch):
        self.text = text
        self.visible = True
        self.label = pyglet.text.Label(text, x, y, anchor_x='left', anchor_y='center', 
                                       color=(0, 0, 0, 255), batch=batch)
        self.bounding_box = pyglet.shapes.Rectangle(x, y, width, height, color=(200, 200, 220), batch=batch)

    def is_mouseover(self, x, y):
        if not self.visible:
            return False
        
        is_within_horizontal_bounds = self.bounding_box.x < x < self.bounding_box.x + self.bounding_box.width
        is_within_vertical_bounds = self.bounding_box.y < y < self.bounding_box.y + self.bounding_box.height

        return is_within_horizontal_bounds and is_within_vertical_bounds
    
    def set_hover(self, x, y):
        if self.is_mouseover(x, y):
            self.bounding_box.color = (150, 150, 170)
        else:
            self.bounding_box.color = (200, 200, 220)
    
    def set_visible(self, visible):
        self.visible = visible
        self.label.visible = visible
        self.bounding_box.visible = visible

class ListBox:
    def __init__(self, items, x, y, width, height, batch):
        self.batch = batch
        self.items_data = items
        self.rows = []
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.scroll_offset = 0
        self.item_height = 30
        self.padding = 20
        self.visible_count = height // self.item_height
        self.last_click_time = 0
        self.last_clicked_row = None
        self.update_table(items)

    def update_table(self, items):
        for item in items:
            self.rows.append(ListRow(item, self.x, 0, self.width, self.item_height, self.batch))
        self.update_row_positions()

    def on_mouse_motion(self, x, y, _dx, _dy):
        for row in self.rows:
            row.set_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for row in self.rows:
            if row.is_mouseover(x, y):
                clicked_row = row
                current_time = time.perf_counter()
                if (clicked_row == self.last_clicked_row and current_time - self.last_click_time < 0.5):
                    self.last_click_time = current_time
                    self.last_clicked_row = None
                    return row.text
                
                self.last_click_time = current_time
                self.last_clicked_row = row
        return None
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.is_mouseover_list_box(x, y):
            max_offset = max(0, len(self.rows) - self.visible_count)
            self.scroll_offset = min(max(0, self.scroll_offset - int(scroll_y)), max_offset)
            self.update_row_positions()
    
    def is_mouseover_list_box(self, x, y):
        is_within_horizontal_bounds = self.x < x < self.x + self.width
        is_within_vertical_bounds = self.y < y < self.y + self.height

        return is_within_horizontal_bounds and is_within_vertical_bounds

    def update_row_positions(self):
        start_index = self.scroll_offset
        end_index = min(start_index + self.visible_count, len(self.rows))
        current_y = self.y + self.height
        
        for i, row in enumerate(self.rows):
            if i < start_index or i >= end_index:
                row.set_visible(False)
                continue
            
            row.set_visible(True)
            row_y = current_y - self.item_height
            row.bounding_box.x = self.x
            row.bounding_box.y = row_y
            row.label.x = self.x + self.padding
            row.label.y = row_y + self.item_height // 2
            current_y -= self.item_height

        
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