# Third-party modules
import pygame
import pygame.locals

# User-defined modules
import pygame_rl.renderer.pygame_renderer as pygame_renderer


class PredatorPreyRenderer(pygame_renderer.TiledRenderer):
    """Predator-prey renderer.
    """
    # Constants
    title = 'Predator-prey'

    # Environment
    env = None

    # Renderer options
    renderer_options = None

    # Display state
    display_quitted = False

    # TMX objects
    static_overlays = None
    moving_overlays = None

    # Clock object (pygame.time.Clock())
    clock = None

    # Dirty groups (pygame.sprite.RenderUpdates)
    dirty_groups = None

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

        # Initialize the moving overlays
        self._load_moving_overlays()

        # Initialize the dirty group
        self._load_dirty_group()

        # Blit the background to the screen
        self.screen.blit(self.background, [0, 0])

        # Update the full display
        if self.renderer_options.show_display:
            pygame.display.flip()

        # Create the clock
        self.clock = pygame.time.Clock()

    def render(self):
        # Close the display if the renderer options is set to disable the
        # display
        if not self.display_quitted and not self.renderer_options.show_display:
            # Replace the screen surface with in-memory surface
            self.screen = self.screen.copy()
            # Close the display
            pygame.display.quit()
            # Prevent from further closing
            self.display_quitted = True

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
                        if event.key == pygame.locals.K_RIGHT:
                            self.env.take_cached_action(0, 'MOVE_RIGHT')
                        elif event.key == pygame.locals.K_UP:
                            self.env.take_cached_action(0, 'MOVE_UP')
                        elif event.key == pygame.locals.K_LEFT:
                            self.env.take_cached_action(0, 'MOVE_LEFT')
                        elif event.key == pygame.locals.K_DOWN:
                            self.env.take_cached_action(0, 'MOVE_DOWN')
                        elif event.key == pygame.locals.K_s:
                            self.env.take_cached_action(0, 'STAND')
                        # Update the state
                        self.env.update_state()

        # Indicate the rendering should continue
        return True

    def _load_moving_overlays(self):
        self.moving_overlays = []
        for group_name in self.env.group_names:
            static_overlay = self.static_overlays[group_name]
            object_index = self.env.get_group_index_range(group_name)
            for _ in range(*object_index):
                moving_overlay = pygame_renderer.OverlaySprite(
                    static_overlay.image, static_overlay.pos,
                    static_overlay.tile_dim)
                self.moving_overlays.append(moving_overlay)

    def _load_dirty_group(self):
        self.dirty_groups = pygame.sprite.RenderUpdates()
        self.dirty_groups.add(self.moving_overlays)

    def _update_overlay_pos(self):
        for object_index in range(self.env.options.get_total_object_size()):
            pos = self.env.state.get_object_pos(object_index)
            self.moving_overlays[object_index].set_pos(pos)

    def _update_overlay_visibility(self):
        for object_index in range(self.env.options.get_total_object_size()):
            availability = self.env.state.get_object_availability(object_index)
            if not availability:
                self.dirty_groups.remove(self.moving_overlays[object_index])


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
