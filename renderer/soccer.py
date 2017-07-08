# Third-party modules
import pygame
import pygame.locals

# User-defined modules
from renderer.pygame_util import TiledRenderer


class Soccer(TiledRenderer):
  """Soccer environment.
  """
  # Constants
  TITLE = 'Soccer'
  MAP_FILENAME = 'data/map/soccer.tmx'
  MAX_FPS = 60

  # Environment state
  env_state = None

  # TMX objects
  tiled_map = None
  overlays = None

  # Clock object (pygame.time.Clock)
  clock = None

  # Surfaces (pygame.Surface)
  screen = None
  background = None

  # Render updates (pygame.sprite.RenderUpdates)
  players = None

  def __init__(self, env_state):
    super().__init__(self.MAP_FILENAME)
    self.env_state = env_state

  def load(self):
    # Initialize Pygame
    pygame.display.init()
    pygame.display.set_mode((400, 300))
    pygame.display.set_caption(self.TITLE)

    # Initialize the renderer
    super().load()

    # Set the screen size
    resolution = super().get_display_size()
    self.screen = pygame.display.set_mode(resolution)

    # Get the background
    self.background = super().get_background()

    # Get the overlay
    self.overlays = super().get_overlays()

    # Create the players sprite group
    self.players = pygame.sprite.RenderUpdates()
    for overlay in self.overlays.values():
      self.players.add(overlay)

    # Blit the background to the screen
    self.screen.blit(self.background, (0, 0))

    # Update the full display
    pygame.display.flip()

    # Create the clock
    self.clock = pygame.time.Clock()

  def render(self):
    # Redraw the overlays
    self.players.clear(self.screen, self.background)
    dirty = self.players.draw(self.screen)

    # Update only the dirty surface
    pygame.display.update(dirty)

    # Limit the max frames per second
    self.clock.tick(self.MAX_FPS)

    # Handle the event
    for event in pygame.event.get():
      if event.type == pygame.locals.QUIT:
        return False
      elif event.type == pygame.locals.K_RIGHT:
        self.env_state.take_action('MOVE_RIGHT')
    return True
