import pyglet
import glooey

class TestWindow:
    def __init__(self):
        # Create window
        self.window = pyglet.window.Window(width=400, height=300, caption="UI Test")
        
        # Initialize UI
        self.gui = glooey.Gui(self.window)
        
        # Create a vertical box for layout
        self.vbox = glooey.VBox()
        self.vbox.alignment = 'center'
        
        # Create test button
        self.test_button = glooey.Button("Test Button")
        self.test_button.push_handlers(on_click=self.on_button_click)
        
        # Add button to layout
        self.vbox.add(self.test_button)
        
        # Add layout to GUI
        self.gui.add(self.vbox)

    def on_button_click(self, widget):
        print("Button clicked!")

    def run(self):
        pyglet.app.run()

if __name__ == "__main__":
    window = TestWindow()
    window.run()