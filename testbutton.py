import pyglet
from pyglet.window import mouse, key

class TextInputWindow(pyglet.window.Window):
    def __init__(self, width=400, height=200, caption="Text Input Demo"):
        super().__init__(width=width, height=height, caption=caption)
        self.set_minimum_size(400, 200)
        
        # The user's input text & focus state
        self.text = ""
        self.focused = False

        # Create a batch to draw shapes
        self.batch = pyglet.graphics.Batch()

        # Create the background rectangle of the text box
        self.box_x, self.box_y = 50, 100
        self.box_width, self.box_height = 300, 40
        self.box_rect = pyglet.shapes.Rectangle(
            self.box_x,
            self.box_y,
            self.box_width,
            self.box_height,
            color=(200, 200, 200),
            batch=self.batch
        )

        # A simple rectangular outline if focused
        self.box_outline = pyglet.shapes.Rectangle(
            self.box_x - 1,
            self.box_y - 1,
            self.box_width + 2,
            self.box_height + 2,
            color=(50, 50, 50),
            batch=self.batch
        )
        # Make outline transparent by default
        self.box_outline.opacity = 0

        # Label to display typed text
        self.label = pyglet.text.Label(
            text=self.text,
            x=self.box_x + 5,
            y=self.box_y + self.box_height//4,
            color=(0, 0, 0, 255),  # black text
        )

    def on_draw(self):
        self.clear()
        # Draw shapes (batch) first
        self.batch.draw()
        # Draw the text label last
        self.label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            # Check if click is inside the text box
            if (self.box_x <= x <= self.box_x + self.box_width
                and self.box_y <= y <= self.box_y + self.box_height):
                self.focused = True
                # Make outline visible
                self.box_outline.opacity = 255
            else:
                self.focused = False
                self.box_outline.opacity = 0

    def on_text(self, text):
        if self.focused:
            self.text += text
            self.label.text = self.text

    def on_key_press(self, symbol, modifiers):
        if self.focused:
            if symbol == key.BACKSPACE and self.text:
                self.text = self.text[:-1]
                self.label.text = self.text
            elif symbol == key.ENTER:
                # “Accept” the text (print to console)
                print("Accepted text:", self.text)
                self.text = ""
                self.label.text = self.text

if __name__ == "__main__":
    window = TextInputWindow()
    pyglet.app.run()