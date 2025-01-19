import pyglet

class SimpleWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)

        self.batch = pyglet.graphics.Batch()
        self.text_background = pyglet.shapes.Rectangle(
            x=10,  # Initial x position
            y=10,  # Initial y position (from bottom)
            width=self.width - 20,  # Width with padding
            height=self.height - 20,  # Height with padding
            color=(255, 255, 255),  # White color
            batch=self.batch
        )

        self.text_document = pyglet.text.document.UnformattedDocument("Edit me!")
        self.text_document.set_style(0, len(self.text_document.text), 
                                   dict(color=(0, 0, 0, 255)))
        
        # Create a layout to display the text document
        self.text_layout = pyglet.text.layout.IncrementalTextLayout(
            self.text_document, 
            width=self.width - 20, 
            height=self.height - 20,
            multiline=True
        )
        
        self.text_layout.x = 10
        self.text_layout.y = self.height - 30
        # Create a caret for user input
        self.caret = pyglet.text.caret.Caret(self.text_layout)
        self.push_handlers(self.caret)

        self.set_visible(True)
        self.set_exclusive_mouse(False)
        self.caret.visible = True
        self.caret.mark = 0
        self.caret.position = len(self.text_document.text)
        self.set_focus(self.text_layout)


    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.text_layout.draw()

    def on_text(self, text):
        # Handle character input
        self.caret.on_text(text)

    def on_text_motion(self, motion):
        # Handle text motion (e.g., arrow keys)
        self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        # Handle text selection
        self.caret.on_text_motion_select(motion)

    def on_resize(self, width, height):
        super().on_resize(width, height)

        # Resize and reposition the text layout dynamically
        self.text_background.width = width - 20
        self.text_background.height = height - 20

        # Resize and reposition the text layout
        self.text_layout.width = width - 20
        self.text_layout.height = height - 20
        self.text_layout.x = 10
        self.text_layout.y = height - 10  # Position from top

    def on_activate(self):
        """Handle window activation."""
        self.caret.visible = True

    def on_deactivate(self):
        """Handle window deactivation."""
        self.caret.visible = False

    def set_focus(self, focus):
        if focus is self.focus:
            return

        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True

if __name__ == "__main__":
    window = SimpleWindow()
    #pyglet.clock.schedule_interval(window.update, 1/60.0)
    pyglet.app.run()