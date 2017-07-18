# Third-party modules
import numpy as np
import pygame
import pygame.locals

# User-defined modules
import pygame_soccer.renderer.pygame_renderer as pygame_renderer


class SoccerRenderer(pygame_renderer.TiledRenderer):
  """Soccer renderer.
  """
  # Constants
  title = 'Soccer'

  # Environment
  env = None

  # Renderer options
  renderer_options = None

  # Display state
  display_quitted = False

  # TMX objects
  overlays = None

  # Clock object (pygame.time.Clock)
  clock = None

  # Surfaces (pygame.Surface)
  screen = None
  background = None

  # Render updates (pygame.sprite.RenderUpdates)
  agents = None

  def __init__(self, map_path, env, renderer_options=None):
    super().__init__(map_path)
    # Save the environment
    self.env = env
    # Use or create the renderer options
    self.renderer_options = renderer_options or RendererOptions()

  def load(self):
    # Initialize Pygame
    pygame.display.init()
    pygame.display.set_mode([400, 300])
    pygame.display.set_caption(self.title)

    # Initialize the renderer
    super().load()

    # Set the screen size
    resolution = super().get_display_size()
    self.screen = pygame.display.set_mode(resolution)

    # Get the background
    self.background = super().get_background()

    # Get the overlay
    self.overlays = super().get_overlays()

    # Create the agent sprite group
    self.agents = pygame.sprite.RenderUpdates()
    for overlay in self.overlays.values():
      self.agents.add(overlay)

    # Blit the background to the screen
    self.screen.blit(self.background, [0, 0])

    # Update the full display
    if self.renderer_options.show_display:
      pygame.display.flip()

    # Create the clock
    self.clock = pygame.time.Clock()

  def render(self):
    # Close the display if the renderer options is set to disable the display
    if not self.display_quitted and not self.renderer_options.show_display:
      # Replace the screen surface with in-memory surface
      self.screen = self.screen.copy()
      # Close the display
      pygame.display.quit()
      # Prevent from further closing
      self.display_quitted = True

    # Clear the overlays
    self.agents.clear(self.screen, self.background)

    # Update the overlays by the environment state
    self.agents.empty()
    for agent_index in range(self.env.options.get_agent_size()):
      name_no_ball = 'AGENT{}'.format(agent_index + 1)
      name_has_ball = 'AGENT{}_BALL'.format(agent_index + 1)
      agent_no_ball = self.overlays[name_no_ball]
      agent_has_ball = self.overlays[name_has_ball]
      # Get the agent state
      agent_pos = self.env.state.get_agent_pos(agent_index)
      has_ball = self.env.state.get_agent_ball(agent_index)
      # Choose the overlay
      if has_ball:
        agent = agent_has_ball
      else:
        agent = agent_no_ball
      # Set the overlay position
      agent.set_pos(agent_pos)
      # Add the sprite to the group
      self.agents.add(agent)

    # Draw the overlays
    dirty = self.agents.draw(self.screen)

    # Update only the dirty surface
    if self.renderer_options.show_display:
      pygame.display.update(dirty)

    # Limit the max frames per second
    if self.renderer_options.show_display:
      self.clock.tick(self.renderer_options.max_fps)

    # Handle the events
    if self.renderer_options.show_display:
      for event in pygame.event.get():
        # Detect the quit event
        if event.type == pygame.locals.QUIT:
          # Indicate the rendering should stop
          return False
        # Detect the keydown event
        if self.renderer_options.enable_key_events:
          if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_RIGHT:
              self.env.take_action(self._get_action('MOVE_RIGHT'))
            elif event.key == pygame.locals.K_UP:
              self.env.take_action(self._get_action('MOVE_UP'))
            elif event.key == pygame.locals.K_LEFT:
              self.env.take_action(self._get_action('MOVE_LEFT'))
            elif event.key == pygame.locals.K_DOWN:
              self.env.take_action(self._get_action('MOVE_DOWN'))

    # Indicate the rendering should continue
    return True

  def get_screenshot(self):
    image = pygame.surfarray.array3d(self.screen)
    # Swap the axes as the X and Y axes in Pygame and Scipy are opposite
    return np.swapaxes(image, 0, 1)

  def _get_action(self, first_player_action):
    action = ['STAND'] * self.env.options.team_size
    action[0] = first_player_action
    return action


class RendererOptions(object):
  """Renderer options.
  """
  show_display = False
  max_fps = 0
  enable_key_events = False

  def __init__(self, show_display=False, max_fps=0, enable_key_events=False):
    self.show_display = show_display
    self.max_fps = max_fps
    self.enable_key_events = enable_key_events
