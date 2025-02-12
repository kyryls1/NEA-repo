import pytest
import pyglet
from vector import Vector
from renderer import Renderer

@pytest.fixture
def test_renderer():
    batch = pyglet.graphics.Batch()
    origin = Vector(100, 200)
    return Renderer(batch, origin, 20, 70, 30, 50)

def test_plot_active_configuration_performance(test_renderer):
    test_renderer.store_graph_point(0, 10, 1000)
    test_renderer.store_graph_point(1, 20, 1500)
    test_renderer.store_graph_point(2, 30, 2000)
    test_renderer.store_paused_point(1)
    test_renderer.store_throttle_change_point(1.5, 0.04)
    test_renderer.store_engine_load_change_point(2, 50)

    named_parameters = ["TestConfig", 50, 5, 100, 2, 40, 60, 0.001, 3]
    test_renderer.plot_active_configuration_performance(named_parameters)

    assert 0 in test_renderer.open_design_plots
    assert test_renderer.open_design_plots[0].is_alive()
