# Third-party modules
import pygame


class TilesetCache(object):
  """Load the tileset into the cache.

  Attributes:
    dim (tuple): The dimension of one tile.
    cache (dict): The tileset cache. The key is the filename, the value is the
    tileset table containing tiles as pygame.Surface.
  """

  dim = None
  cache = {}

  def __init__(self, dim):
    self.dim = dim

  def __getitem__(self, filename):
    try:
      return self.cache[filename]
    except KeyError:
      tile_table = self._load_tileset(filename)
      self.cache[filename] = tile_table
      return tile_table

  def _load_tileset(self, filename):
    # Get the dimension
    (width, height) = self.dim
    # Load the image
    image = load_image(filename)
    # Get the image size
    (image_width, image_height) = image.get_size()
    # Load the tiles in the tileset
    tileset = []
    for x_tile in range(0, image_width // width):
      col = []
      for y_tile in range(0, image_height // height):
        # Get a tile as a subsurface from the image as the surface
        rect = (width * x_tile, height * y_tile, width, height)
        tile = image.subsurface(rect)
        col.append(tile)
      tileset.append(col)
    return tileset


def load_image(filename):
  """Load an image by Pygame.

  Args:
    filename (str): The image.

  Returns:
    pygame.Surface: The Pygame surface.
  """
  try:
    image = pygame.image.load(filename)
    if not image.get_alpha():
      image = image.convert()
    else:
      image = image.convert_alpha()
  except pygame.error:
    print('Cannot load the image {}'.format(filename))
    raise SystemExit
  return image
