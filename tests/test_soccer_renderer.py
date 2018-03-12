# Third-party modules
import pygame

# Testing targets
import pygame_rl.scenario.soccer_environment as soccer_environment


class SoccerRendererTest(object):
    renderer = None

    @classmethod
    def setup_class(cls):
        env = soccer_environment.SoccerEnvironment()
        cls.renderer = env.renderer

    def test_load(self):
        self.renderer.load()
        # Check the types of the attributes
        assert isinstance(self.renderer.static_overlays, dict)
        assert not self.renderer.clock is None
        assert isinstance(self.renderer.screen, pygame.Surface)
        assert isinstance(self.renderer.background, pygame.Surface)
        assert isinstance(self.renderer.dirty_groups,
                          pygame.sprite.RenderUpdates)

    def test_render(self):
        # The renderer should indicate to continue
        assert self.renderer.render()
        # The display should have quitted
        assert self.renderer.display_quitted
        # The agent sprites should contain exactly 2 sprites
        assert len(self.renderer.dirty_groups.sprites()) == 2

    def test_get_screenshot(self):
        # Get the display size
        display_size = self.renderer.get_display_size()
        # Get the entire screenshot
        screenshot = self.renderer.get_screenshot()
        # The returned screenshot should have opposite axes and 3 channels
        assert screenshot.shape == (display_size[1], display_size[0], 3)

    def test_get_po_screenshot(self):
        # Get the display size
        tile_size = self.renderer.get_tile_size()
        # Specify the agent index
        agent_index = 0
        # Get the partially observable screenshot of the first agent with a
        # radius of 0
        radius = 0
        po_screenshot = self.renderer.get_po_screenshot(agent_index, radius)
        assert po_screenshot.shape == (1 * tile_size[1], 1 * tile_size[0], 3)
        # Get the partially observable screenshot of the first agent with a
        # radius of 1
        radius = 1
        po_screenshot = self.renderer.get_po_screenshot(agent_index, radius)
        assert po_screenshot.shape == (3 * tile_size[1], 3 * tile_size[0], 3)
        # Get the partially observable screenshot of the first agent with a
        # radius of 2
        radius = 2
        po_screenshot = self.renderer.get_po_screenshot(agent_index, radius)
        assert po_screenshot.shape == (5 * tile_size[1], 5 * tile_size[0], 3)
        # Get the partially observable screenshot of the first agent with a
        # radius of 10
        radius = 10
        po_screenshot = self.renderer.get_po_screenshot(agent_index, radius)
        assert po_screenshot.shape == (21 * tile_size[1], 21 * tile_size[0], 3)
