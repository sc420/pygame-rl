# Third-party modules
import numpy as np
import pygame
import pygame.locals
import pytmx

# User-defined modules
from renderer.pygame_util import TiledRenderer
from soccer.renderer_options import RendererOptions


class SoccerRenderer(TiledRenderer):
  """Soccer renderer.
  """
  # Constants
  title = 'Soccer'

  # Environment state
  env_state = None

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

  def __init__(self, map_path, env_state, renderer_options=None):
    super().__init__(map_path)
    # Save the environment state
    self.env_state = env_state
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
    # Uninitialize the display if the renderer options is set to disable the
    # display
    if not self.display_quitted and not self.renderer_options.show_display:
      # Replace the screen surface with in-memory surface
      self.screen = self.screen.copy()
      # Uninitialize the display
      pygame.display.quit()
      # Prevent from further unitialization
      self.display_quitted = True

    # Clear the overlays
    self.agents.clear(self.screen, self.background)

    # Update the overlays by the environment state
    self.agents.empty()
    agent1 = self.overlays['agent1']
    agent1_ball = self.overlays['agent1_ball']
    agent2 = self.overlays['agent2']
    agent2_ball = self.overlays['agent2_ball']
    agent_obj = [
        [agent1, agent1_ball],
        [agent2, agent2_ball],
    ]
    for agent_ind in range(2):
      # Get the agent state
      agent_list = agent_obj[agent_ind]
      agent_pos = self.env_state.state.get_agent_pos(agent_ind)
      has_ball = self.env_state.state.get_agent_ball(agent_ind)
      # Choose the agent
      agent = agent_list[1 if has_ball else 0]
      # Set the agent position
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
              self.env_state.take_action('MOVE_RIGHT')
            elif event.key == pygame.locals.K_UP:
              self.env_state.take_action('MOVE_UP')
            elif event.key == pygame.locals.K_LEFT:
              self.env_state.take_action('MOVE_LEFT')
            elif event.key == pygame.locals.K_DOWN:
              self.env_state.take_action('MOVE_DOWN')
            elif event.key == pygame.locals.K_1:
              self.env_state.state.set_agent_ball(0, True)
            elif event.key == pygame.locals.K_2:
              self.env_state.state.set_agent_ball(0, False)

    # Indicate the rendering should continue
    return True

  def get_screenshot(self):
    image = pygame.surfarray.array3d(self.screen)
    # Swap the axes as the X and Y axes in Pygame and Scipy are opposite
    return np.swapaxes(image, 0, 1)
