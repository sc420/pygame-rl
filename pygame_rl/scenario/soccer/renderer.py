# Third-party modules
import pygame
import pygame.locals

# User-defined modules
from pygame_rl.renderer.pygame_renderer import TiledRenderer
from pygame_rl.scenario.soccer.renderer_options import RendererOptions


class Renderer(TiledRenderer):
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
    static_overlays = None

    # Clock object (pygame.time.Clock())
    clock = None

    # Dirty groups (pygame.sprite.RenderUpdates)
    dirty_groups = None

    # Previous ball state
    prev_ball_state = None

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

        # Get the static overlays
        self.static_overlays = super().get_overlays()

        # Initialize previous ball state
        self._init_prev_ball_state()

        # Initialize the dirty group
        self._load_dirty_group()

        # Blit the background to the screen
        self.screen.blit(self.background, [0, 0])

        # Update the full display
        if self.renderer_options.show_display:
            pygame.display.flip()

        # Create the clock
        self.clock = pygame.time.Clock()

        # Close the display if the renderer options is set to disable the
        # display
        if not self.display_quitted and not self.renderer_options.show_display:
            # Replace the screen surface with in-memory surface
            self.screen = self.screen.copy()
            # Close the display
            pygame.display.quit()
            # Prevent from further closing
            self.display_quitted = True

    def render(self):
        # Clear the overlays
        self.dirty_groups.clear(self.screen, self.background)

        # Update the overlays by the environment state
        self._update_overlay_pos()
        self._update_overlay_visibility()

        # Draw the overlays
        dirty = self.dirty_groups.draw(self.screen)

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
                        # Get the agent index of the first player
                        team_agent_index = 0
                        agent_index = self.env.get_agent_index(
                            'PLAYER', team_agent_index)
                        # Prepare the cached action
                        cached_action = None
                        if event.key == pygame.locals.K_RIGHT:
                            cached_action = 'MOVE_RIGHT'
                        elif event.key == pygame.locals.K_UP:
                            cached_action = 'MOVE_UP'
                        elif event.key == pygame.locals.K_LEFT:
                            cached_action = 'MOVE_LEFT'
                        elif event.key == pygame.locals.K_DOWN:
                            cached_action = 'MOVE_DOWN'
                        elif event.key == pygame.locals.K_s:
                            cached_action = 'STAND'
                        # Take the cached action and update the state
                        if cached_action:
                            self.env.take_cached_action(
                                agent_index, cached_action)
                            self.env.update_state()

        # Indicate the rendering should continue
        return True

    def _init_prev_ball_state(self):
        agent_size = self.env.options.agent_size
        self.prev_ball_state = agent_size * [None]

    def _load_dirty_group(self):
        self.dirty_groups = pygame.sprite.RenderUpdates()

    def _update_overlay_pos(self):
        for agent_index in range(self.env.options.agent_size):
            [overlay_has_ball, overlay_no_ball] = self._get_overlays(
                agent_index)
            has_ball = self.env.state.get_agent_ball(agent_index)
            agent_pos = self.env.state.get_agent_pos(agent_index)
            if has_ball:
                overlay_has_ball.set_pos(agent_pos)
            else:
                overlay_no_ball.set_pos(agent_pos)

    def _update_overlay_visibility(self):
        for agent_index in range(self.env.options.agent_size):
            # Get the static overlays
            [overlay_has_ball, overlay_no_ball] = self._get_overlays(
                agent_index)
            # Check whether the agent has the ball
            has_ball = self.env.state.get_agent_ball(agent_index)
            # Get the previous ball state
            prev_has_ball = self.prev_ball_state[agent_index]
            # Check whether the ball state has changed
            if prev_has_ball is None or prev_has_ball != has_ball:
                # Remove the old sprite and add the new sprite in the dirty
                # group
                if has_ball:
                    self.dirty_groups.remove(overlay_no_ball)
                    self.dirty_groups.add(overlay_has_ball)
                else:
                    self.dirty_groups.remove(overlay_has_ball)
                    self.dirty_groups.add(overlay_no_ball)
                # Set the previous ball state
                self.prev_ball_state[agent_index] = has_ball

    def _get_overlays(self, agent_index):
        name_has_ball = 'AGENT{}_BALL'.format(agent_index + 1)
        name_no_ball = 'AGENT{}'.format(agent_index + 1)
        overlay_has_ball = self.static_overlays[name_has_ball]
        overlay_no_ball = self.static_overlays[name_no_ball]
        return [overlay_has_ball, overlay_no_ball]
