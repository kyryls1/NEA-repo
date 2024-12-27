import pyglet
from pyglet.gui import PushButton
import math
 
class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y
   
    def rotate(self, angle):
        new_x = self.x * math.cos(angle) + self.y * -math.sin(angle)
        new_y = self.x * math.sin(angle) + self.y * math.cos(angle)
        self.x, self.y = new_x, new_y
       
    def angle_between(self, vector2):
        dot_product = self.x * vector2.x + self.y * vector2.y
        return math.acos(dot_product / (self.modulus() * vector2.modulus()))
   
    def modulus(self):
        return math.sqrt(self.x**2 + self.y**2)
 
class Crank():
    def __init__(self, radius, mass, batch):
        # crank = pyglet.image.load('testsprite.png')   add later if I use actual sprite
        # crank.anchor_x = round(crank.width / 2)
        # crank.anchor_y = round(crank.height / 2)
 
        self.crankarm = pyglet.shapes.Line(x=400, y=400, x2=400, y2=520, width=40, color=[255, 255, 255], batch=batch)
        self.bearing = pyglet.shapes.Circle(x=400, y=400, radius=20, color=[255, 255, 255], batch=batch)
 
        self.RADIUS = radius
        self.MASS = mass
        self.MOMENT_OF_INTERTIA = self.MASS * self.RADIUS**2
 
        self.angular_velocity = 2 # fix to start properly later, but have this here so the engine actually starts
        self.angle_radians = 0
 
    def update_angle(self, delta_theta):
        self.angle_radians += delta_theta
        self.angle_radians %= (2 * math.pi)

        angle_degrees = math.degrees(self.angle_radians)
        self.crankarm.rotation = angle_degrees
        self.bearing.rotation = angle_degrees
 
    def get_delta_theta(self, dt):
        return self.angular_velocity * dt
   
    def get_torque(self, force):
        return force * self.RADIUS
 
    def update_angular_velocity(self, torque, dt):
        angular_momentum_change = torque * dt
        angular_velocity_change = angular_momentum_change / self.MOMENT_OF_INTERTIA
        self.angular_velocity += angular_velocity_change
 
    def update(self, force, dt):
        torque = self.get_torque(force)
        #print(torque)
        self.update_angular_velocity(torque, dt)
        self.update_angle(self.get_delta_theta(dt))
 
class ConnectorRod():
    def __init__(self, mass, batch):
        self.rod = pyglet.shapes.Line(x=400, y=500, x2=400, y2=700, width=15, color=[201, 201, 201], batch=batch)
        self.crank_bearing = pyglet.shapes.Circle(x=400, y=500, radius=15, color=[201, 201, 201], batch=batch)
        self.piston_bearing = pyglet.shapes.Circle(x=400, y=700, radius=15, color=[201, 201, 201], batch=batch)
       
        self.MASS = mass
        self.LENGTH = 200 #Remember to change this later!!
        self.crank_anchor_vector = Vector(0, 100)
 
    def update_crank_anchor_position(self, delta_theta):
        initial_x = self.crank_anchor_vector.x
        initial_y = self.crank_anchor_vector.y

        self.crank_anchor_vector.rotate(-delta_theta) # use negative theta as the matrix rotation is clockwise
        delta_x = self.crank_anchor_vector.x - initial_x
        delta_y = self.crank_anchor_vector.y - initial_y

        self.rod.x += delta_x
        self.rod.y += delta_y
        self.crank_bearing.x += delta_x
        self.crank_bearing.y += delta_y
 
    def update_piston_anchor_position(self):
        delta_x = self.rod.x2 - self.rod.x
        self.rod.y2 = math.sqrt(self.LENGTH**2 - delta_x**2) + self.rod.y
        self.piston_bearing.y = self.rod.y2
   
    def update(self, delta_theta):
        self.update_crank_anchor_position(delta_theta)
        self.update_piston_anchor_position()

class Piston():
    def __init__(self, radius, mass, batch):
        self.RADIUS = radius * 100 #CHANGE THIS TO BE TO SCALE LATER!!
        self.MASS = mass

        self.piston = pyglet.shapes.Rectangle(x=400-self.RADIUS, y=700, width=self.RADIUS*2, height=150, color=[255, 255, 255], batch=batch)

    def update(self, y_coordinate):
        self.piston.y = y_coordinate

 
class Simulation():
    def __init__(self, radius, crank_mass, rod_mass, piston_mass, piston_radius):
        self.batch = pyglet.graphics.Batch()
 
        self.crank = Crank(radius, crank_mass, self.batch)
        self.rod = ConnectorRod(rod_mass, self.batch)
        self.piston = Piston(piston_mass,  piston_radius, self.batch)

        self.component_weight = (rod_mass + piston_mass) * 9.81

    def draw(self):
        self.batch.draw()
 
    def update_all(self, dt):
        global force
        if self.crank.angle_radians > math.pi:
            force = 0.3
        else:
            force = 1

        rod_direction_vector = self.find_rod_direction_vector()
        force_parallel_to_rod = self.transfer_force_to_rod(force, rod_direction_vector)
        force_tangent_to_crank = self.transfer_force_to_crank(force_parallel_to_rod, rod_direction_vector)

        self.crank.update(force_tangent_to_crank, dt)  #make sure you replace the constant torque with the actual torque value
        self.rod.update(self.crank.get_delta_theta(dt))
        self.piston.update(self.rod.rod.y2)
 
    def find_normal_to_crank_motion(self, theta):
        if theta == math.pi/2:
            return Vector(0, 1)
        else:
            return Vector(1, math.tan(theta))
   
    def find_rod_direction_vector(self):
        return Vector(self.rod.rod.x2 - self.rod.rod.x, self.rod.rod.y2 - self.rod.rod.y) #this naming convention looks so stupid
    
    def transfer_force_to_rod(self, force, rod_direction_vector):
        piston_to_rod_angle = rod_direction_vector.angle_between(Vector(0, 1))
        total_downward_force = force + self.component_weight

        return math.cos(piston_to_rod_angle) * total_downward_force
 
    def transfer_force_to_crank(self, force, rod_direction_vector):
        normalised_angle = (-self.crank.angle_radians + math.pi/2) % (2 * math.pi)
        normal_to_crank_motion = self.find_normal_to_crank_motion(normalised_angle)
        rod_to_crank_angle = 3 * math.pi / 2 - normal_to_crank_motion.angle_between(rod_direction_vector)

        if self.crank.angle_radians < math.pi:
            return -math.cos(rod_to_crank_angle) * force
        else:
            return math.cos(rod_to_crank_angle) * force

class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(width=400, height=300)

        # Placeholder for Simulation
        self.simulation = Simulation(1, 1, 1, 1, 1)

        # Load images for the button states
        self.pressed_image = pyglet.resource.image('testsprite.png')
        self.depressed_image = pyglet.resource.image('testsprite.png')

        # Create a batch for rendering GUI elements
        self.batch = pyglet.graphics.Batch()

        # Create a PushButton
        self.radius_input = PushButton(
            x=100,
            y=100,
            pressed=self.pressed_image,
            depressed=self.depressed_image,
            batch=self.batch
        )

        # Button position and size for manual hit detection
        self.button_x = 100
        self.button_y = 100
        self.button_width = self.depressed_image.width
        self.button_height = self.depressed_image.height

    def change_radius(self):
        print("Button pressed!")

    def on_draw(self):
        self.clear()
        self.simulation.draw()  # Render simulation graphics
        self.batch.draw()  # Draw the batch containing GUI elements

    def on_mouse_press(self, x, y, button, modifiers):
        # Check if the mouse click is within the button bounds
        if (self.button_x <= x <= self.button_x + self.button_width and self.button_y <= y <= self.button_y + self.button_height
        ):
            self.change_radius()

    def update(self, dt):
        self.simulation.update_all(dt)
 
if __name__ == "__main__":
    force = 1
    simulation = SimulationWindow(width=1280, height=720, caption="Simulation", resizable = True)
    pyglet.clock.schedule_interval(simulation.update, 1/60)
    pyglet.app.run()
