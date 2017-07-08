# Third-party modules
from pytmx.util_pygame import load_pygame
import pygame
import pygame.locals

# User-defined modules
from renderer.pygame_util import TilesetCache
import renderer.file_util as file_util

# Global constants
MAX_FPS = 60
MAP_TILE_WIDTH = 24
MAP_TILE_HEIGHT = 16


class Sprite(pygame.sprite.Sprite):
  def __init__(self, pos=(0, 0), frames=None):
    super(Sprite, self).__init__()
    self.image = frames[0][0]
    self.rect = self.image.get_rect()
    self.pos = pos

  def _get_pos(self):
    """Check the current position of the sprite on the map."""

    return (self.rect.midbottom[0] - 12) / 24, (self.rect.midbottom[1] - 16) / 16

  def _set_pos(self, pos):
    """Set the position and depth of the sprite on the map."""

    self.rect.midbottom = (pos[0] * 24 + 12, pos[1] * 16 + 16)
    self.depth = self.rect.midbottom[1]

  pos = property(_get_pos, _set_pos)

  def move(self, dx, dy):
    """Change the position of the sprite on screen."""

    self.rect.move_ip(dx, dy)
    self.depth = self.rect.midbottom[1]


class Level(object):
  tileset_cache = None
  tileset_filename = None

  map = None
  key = {}
  config = None

  level = None
  block = None

  def load_file(self, filename, tileset_cache):
    self.tileset_cache = tileset_cache
    self.config = file_util.read_yaml(filename)
    self.tileset_filename = self.config['level']['tileset']
    self.map = self.config['level']['map'].split('\n')
    self.key = self.config['block']
    self.width = len(self.map[0])
    self.height = len(self.map)

    self.items = {}
    for y, line in enumerate(self.map):
      for x, c in enumerate(line):
        if not self.is_wall(x, y) and 'sprite' in self.key[c]:
          self.items[(x, y)] = self.key[c]

  def get_tile(self, x, y):
    try:
      char = self.map[y][x]
    except IndexError:
      return {}
    try:
      return self.key[char]
    except KeyError:
      return {}

  def get_bool(self, x, y, name):
    """Tell if the specified flag is set for position on the map."""

    value = self.get_tile(x, y).get(name)
    return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

  def is_wall(self, x, y):
    """Is there a wall?"""

    return self.get_bool(x, y, 'wall')

  def render(self):
    wall = self.is_wall
    tiles = self.tileset_cache[self.tileset_filename]
    image = pygame.Surface(
        (self.width * MAP_TILE_WIDTH, self.height * MAP_TILE_HEIGHT))
    overlays = {}
    for map_y, line in enumerate(self.map):
      for map_x, c in enumerate(line):
        if wall(map_x, map_y):
          # Draw different tiles depending on neighbourhood
          if not wall(map_x, map_y + 1):
            if wall(map_x + 1, map_y) and wall(map_x - 1, map_y):
              tile = 1, 2
            elif wall(map_x + 1, map_y):
              tile = 0, 2
            elif wall(map_x - 1, map_y):
              tile = 2, 2
            else:
              tile = 3, 2
          else:
            if wall(map_x + 1, map_y + 1) and wall(map_x - 1, map_y + 1):
              tile = 1, 1
            elif wall(map_x + 1, map_y + 1):
              tile = 0, 1
            elif wall(map_x - 1, map_y + 1):
              tile = 2, 1
            else:
              tile = 3, 1
          # Add overlays if the wall may be obscuring something
          if not wall(map_x, map_y - 1):
            if wall(map_x + 1, map_y) and wall(map_x - 1, map_y):
              over = 1, 0
            elif wall(map_x + 1, map_y):
              over = 0, 0
            elif wall(map_x - 1, map_y):
              over = 2, 0
            else:
              over = 3, 0
            overlays[(map_x, map_y)] = tiles[over[0]][over[1]]
        else:
          try:
            tile = self.key[c]['tile'].split(',')
            tile = int(tile[0]), int(tile[1])
          except (ValueError, KeyError):
            # Default to ground tile
            tile = 0, 3
        tile_image = tiles[tile[0]][tile[1]]
        image.blit(tile_image,
                   (map_x * MAP_TILE_WIDTH, map_y * MAP_TILE_HEIGHT))
    return image, overlays


class Level2(object):
  def render(self):
    pass


class Soccer(object):
  """Soccer environment.
  """

  # Constants
  MAP_FILENAME = 'data/map/soccer.tmx'

  # Tileset cache
  tileset_cache = None

  # Map
  tiled_map = None

  # The clock object (pygame.time.Clock)
  clock = None

  # The surfaces (pygame.Surface)
  screen = None
  background = None
  sprites = None
  overlays = None

  def init(self):
    # Initialize Pygame
    pygame.display.init()
    pygame.display.set_caption('Soccer')
    pygame.display.set_mode((400, 300))

    # Load the tiled map
    self.tiled_map = load_pygame(self.MAP_FILENAME)

    # Initialize the screen
    self.screen = pygame.display.set_mode((424, 320))

    # Initialize the tileset cache
    tile_dim = (MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
    self.tileset_cache = TilesetCache(tile_dim)

    # Initialize the level
    level = Level()
    level.load_file('data/level.yaml', self.tileset_cache)

    # Load the sprite
    sprite_cache = TilesetCache((32, 32))
    self.sprites = pygame.sprite.RenderUpdates()
    for pos, tile in level.items.items():
      sprite = Sprite(pos, sprite_cache[tile["sprite"]])
      self.sprites.add(sprite)

    # Create the clock
    self.clock = pygame.time.Clock()

    self.background, overlay_dict = level.render()
    self.overlays = pygame.sprite.RenderUpdates()
    for ((x, y), image) in overlay_dict.items():
      overlay = pygame.sprite.Sprite(self.overlays)
      overlay.image = image
      overlay.rect = image.get_rect().move(x * 24, y * 16 - 16)

    # Blit everything to the screen
    self.screen.blit(self.background, (0, 0))
    # Draw the overlays on the screen
    self.overlays.draw(self.screen)
    # Update the full display to the screen
    pygame.display.flip()

  def render(self):
    # Redraw the sprites
    self.sprites.clear(self.screen, self.background)
    dirty = self.sprites.draw(self.screen)
    # Draw the overlays on the screen
    self.overlays.draw(self.screen)
    # Update only the dirty surface
    pygame.display.update(dirty)
    # Limit the max frames per second
    self.clock.tick(MAX_FPS)
    # Handle the event
    for event in pygame.event.get():
      if event.type == pygame.locals.QUIT:
        return False
    return True
