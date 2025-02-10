import time
import pyglet
from simulation import Simulation

class FrameRateTestWindow(pyglet.window.Window):
    def __init__(self, simulation, target_fps, total_updates, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulation = simulation
        self.target_fps = target_fps
        self.stabilisation_time = 3 * target_fps # 3 seconds to allow frame rate to stabilise
        self.updates_count_target = total_updates + self.stabilisation_time
        self.updates_count = 0
        self.start_time = None

    def on_draw(self):
        self.clear()

    def scheduled_update(self, dt):
        if self.updates_count == self.stabilisation_time:
            self.start_time = time.perf_counter()
        self.simulation.update_all(dt)
        self.updates_count += 1
        if self.updates_count >= self.updates_count_target:
            pyglet.app.exit()

def test_simulation_refresh_rate():
    test_simulation = Simulation(0.05, 5, 0.1, 2, 0.04, 3, 0.06, 0.001)

    target_fps = 3000
    test_duration_seconds = 10
    expected_updates = target_fps * test_duration_seconds
    dt = 1 / target_fps

    window = FrameRateTestWindow(test_simulation, target_fps, expected_updates, visible=False)
    pyglet.clock.schedule_interval(window.scheduled_update, dt)
    pyglet.app.run()

    elapsed_time = time.perf_counter() - window.start_time
    achieved_fps = window.updates_count / elapsed_time if elapsed_time > 0 else 0

    # Require at least 90% of target framerate
    assert achieved_fps >= target_fps * 0.9, f"Achieved {achieved_fps:.2f} FPS, below 90% of {target_fps}"
    print(f"Achieved FPS: {achieved_fps:.2f}")
