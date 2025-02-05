from widgets import ListTable, ListRow, TextBox, Button
import pyglet

# Test is_mouseover with coordinates inside bounding box
test_batch = pyglet.graphics.Batch()
callback_called = False
def test_callback():
    global callback_called
    callback_called = True
"""
assert test_button.is_mouseover(120, 115) == True
print("Coordinates inside button bounds")
print("Unit Test Passed")

# Test is_mouseover with coordinates outside bounding box
assert test_button.is_mouseover(90, 115) == False  # Left of button
assert test_button.is_mouseover(160, 115) == False  # Right of button
assert test_button.is_mouseover(120, 90) == False   # Below button
assert test_button.is_mouseover(120, 140) == False  # Above button
print("Coordinates outside button bounds")
print("Unit Test Passed")

# Test is_mouseover with coordinates on button boundaries
assert test_button.is_mouseover(100, 115) == False  # Left edge
assert test_button.is_mouseover(150, 115) == False  # Right edge
assert test_button.is_mouseover(120, 100) == False  # Bottom edge
assert test_button.is_mouseover(120, 130) == False  # Top edge
print("Coordinates on button boundaries")
print("Unit Test Passed")
"""'''
# Test set_hover with mouse inside bounding box
test_button = Button("Test", 100, 100, 50, 30, test_callback, test_batch)
test_button.set_hover(125, 115)
assert test_button.bounding_box.color == (150, 150, 170, 255)
print(test_button.bounding_box.color)
test_button.set_hover(90, 115)
assert test_button.bounding_box.color == (200, 200, 220, 255)
print(test_button.bounding_box.color)
print("Unit Test Passed")

# Test callback function
test_button = Button("Test", 100, 100, 50, 30, test_callback, test_batch)
test_button.on_click()
assert callback_called == True
print(callback_called)
print("Unit Test Passed")
''''''

# Test ListRow initialization
test_batch = pyglet.graphics.Batch()
test_data = (1, "Test Label")  # Mock data tuple
test_row = ListRow(test_data, 100, 100, 200, 30, test_batch)
assert test_row.data == test_data
assert test_row.visible == True
assert test_row.label.text == "Test Label"
assert test_row.label.x == 100
assert test_row.label.y == 100
assert test_row.focused == False
assert test_row.bounding_box.color == (200, 200, 220, 255)
print("ListRow correctly initialised")
print("Unit Test Passed")

# Test set_visible
test_row = ListRow(test_data, 100, 100, 200, 30, test_batch)
test_row.set_visible(False)
assert test_row.visible == False
assert test_row.label.visible == False
assert test_row.bounding_box.visible == False
print("Correctly set invisible")
test_row.set_visible(True)
assert test_row.visible == True
assert test_row.label.visible == True
assert test_row.bounding_box.visible == True
print("Correctly set visible")
print("Unit Test Passed")

# Test toggle_focus
test_row = ListRow(test_data, 100, 100, 200, 30, test_batch)
test_row.toggle_focus()
assert test_row.focused == True
assert test_row.bounding_box.color == (127, 127, 145, 255)
print(test_row.bounding_box.color)
test_row.toggle_focus()
assert test_row.focused == False
assert test_row.bounding_box.color == (200, 200, 220, 255)
print(test_row.bounding_box.color)
print("Unit Test Passed")

# Test set_hover behavior
test_row = ListRow(test_data, 100, 100, 200, 30, test_batch)
# Test when focused (should not change color)
test_row.toggle_focus()
test_row.set_hover(150, 115)  # Inside bounds
assert test_row.bounding_box.color == (127, 127, 145, 255)
test_row.set_hover(50, 115)   # Outside bounds
assert test_row.bounding_box.color == (127, 127, 145, 255)
# Test when unfocused
test_row.toggle_focus()
test_row.set_hover(150, 115)  # Inside bounds
assert test_row.bounding_box.color == (150, 150, 170, 255)
test_row.set_hover(50, 115)   # Outside bounds
assert test_row.bounding_box.color == (200, 200, 220, 255)
print("ListRow hover behavior")
print("Unit Test Passed")
''''''
# Test ListTable insert_rows with None data
test_batch = pyglet.graphics.Batch()
test_table = ListTable(None, 100, 100, 380, 210, test_batch)

function_return = test_table.insert_rows(None)
assert function_return == None
print(function_return)
print("Unit Test Passed")

# Test get_focused_data with no focused row
test_table = ListTable(None, 100, 100, 380, 210, test_batch)
test_table.focused_row = None
focused_data = test_table.get_focused_data()
assert focused_data == None
print(focused_data)
print("Unit Test Passed")

# Test get_focused_data with focused row
test_data = (1, "Test Row")
test_row = ListRow(test_data, 120, 100, 380, 30, test_batch)
test_table.focused_row = test_row
focused_data = test_table.get_focused_data()
assert focused_data == test_data
print(focused_data)
print("Unit Test Passed")

# Test on_mouse_motion hover states
test_table = ListTable(None, 100, 100, 380, 210, test_batch)
row1 = ListRow((1, "Row 1"), 120, 280, 380, 30, test_batch)
row2 = ListRow((2, "Row 2"), 120, 250, 380, 30, test_batch)
test_table.rows = [row1, row2]

test_table.on_mouse_motion(150, 295)
assert row1.bounding_box.color == (150, 150, 170, 255)
assert row2.bounding_box.color == (200, 200, 220, 255)
print(row1.bounding_box.color, row2.bounding_box.color)
print("Unit Test Passed")

test_table = ListTable(None, 100, 100, 380, 210, test_batch)
row1 = ListRow((1, "Row 1"), 120, 280, 380, 30, test_batch)
row2 = ListRow((2, "Row 2"), 120, 250, 380, 30, test_batch)
test_table.rows = [row1, row2]

test_table.on_mouse_motion(150, 250)
assert row1.bounding_box.color == (200, 200, 220, 255)
assert row2.bounding_box.color == (200, 200, 220, 255)
print(row1.bounding_box.color, row2.bounding_box.color)
print("Unit Test Passed")
'''

# Test TextBox set_current_value with None
test_batch = pyglet.graphics.Batch()
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
test_textbox.set_current_value(None)
assert test_textbox.current_value_label.text == ""
print(type(test_textbox.current_value_label.text))
print("Unit Test Passed")

# Test TextBox set_current_value with value
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
test_textbox.set_current_value(42)
assert test_textbox.current_value_label.text == "Current: 42"
print(test_textbox.current_value_label.text)
print("Unit Test Passed")

# Test TextBox is_mouseover inside bounds
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
is_mouseover = test_textbox.is_mouseover(150, 110)
assert is_mouseover == True
print(is_mouseover)
print("Unit Test Passed")

# Test TextBox is_mouseover outside bounds
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
is_mouseover = test_textbox.is_mouseover(50, 110)
assert is_mouseover == False  # Left of textbox
print(is_mouseover)
print("Unit Test Passed")

# Test TextBox set_focus
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
test_textbox.set_focus()
assert test_textbox.caret.visible == True
assert test_textbox.caret.position == 0
print(test_textbox.caret.visible, test_textbox.caret.position)
print("Unit Test Passed")

# Test TextBox clear_focus
test_textbox = TextBox("Test Label", 100, 100, 200, test_batch)
test_textbox.set_focus()
test_textbox.clear_focus()
assert test_textbox.caret.visible == False
print(test_textbox.caret.visible)
print("Unit Test Passed")