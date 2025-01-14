import pyglet
window = pyglet.window.Window(width=800, height=600, caption='Input Testing')
batch = pyglet.graphics.Batch()
pyglet.gl.glClearColor(0.8,0.8,0.8,1.0)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    text_entry.focus = True # set focus to the text entry every time the screen is redrawn.  

def text_entry_handler(text):
    text_entry_label.text = f"Text: {text}"

frame = pyglet.gui.Frame(window, order=4)

text_entry = pyglet.gui.TextEntry("Enter Your Name", 100, 100, 150, batch=batch)
text_entry.set_handler('on_commit', text_entry_handler) 

frame.add_widget(text_entry)
text_entry_label = pyglet.text.Label("Text: None", 300, 100, batch=batch)
pyglet.app.run()