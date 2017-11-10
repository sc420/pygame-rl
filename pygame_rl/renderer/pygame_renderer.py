# Native modules
import abc

# Third-party modules
import numpy as np
import pygame
import pytmx
import pytmx.util_pygame

# User-defined modules
import pygame_rl.util.file_util as file_util


class TiledLoader(metaclass=abc.ABCMeta):
  # Map filename
  filename = None

  # Map
  tiled_map = None

  # Layers in the map
  layers = None

  def __init__(self, filename):
    self.filename = filename

  def load_layers(self):
    """Load the layers.

    Layers will be categorized based on the layer property. Layers are
    categorized into either "background" or "overlay" if the boolean property
    exists and is enabled. All layers will be added to the "all" category.

    """
    self.layers = {
        'all': [],
        'background': [],
        'overlay': [],
    }
    for layer in self.tiled_map.layers:
      # Add the layer to all category
      self.layers['all'].append(layer)
      # Categorize based on the property
      prop = layer.properties
      if 'background' in prop and prop['background'] == 'true':
        self.layers['background'].append(layer)
      elif 'overlay' in prop and prop['overlay'] == 'true':
        self.layers['overlay'].append(layer)


class TiledData(TiledLoader):
  def __init__(self, filename):
    super().__init__(filename)

  def load(self):
    # Load the tiled map
    self.tiled_map = pytmx.TiledMap(self.filename)

    # Load the layers
    self.load_layers()

  def get_tile_positions(self):
    """Get the tile positions.

    A tile mapping file can be associated with each layer containing the tile
    types. If the property "tile" exists, with the value of the file path
    relative to the map path, the contents of the mapping from tile name to tid
    (tile ID) will be read; Otherwise, the 2nd mapping will be an empty dict.

    Returns:
      dict: 1st mapping is from the layer name to the 2nd dict. 2nd mapping is
      from the name to the tile positions.
    """
    # Get the background layer
    layers = self.layers['all']
    # Build the mapping
    tile_pos = {}
    for layer in layers:
      # Check whether the tile mapping property exists
      if 'tile' in layer.properties:
        # Get the tile file path relative to the map file
        path = layer.properties['tile']
        resolved_path = file_util.resolve_path(self.filename, path)
        # Read the tile file
        tile_name_to_tid = file_util.read_yaml(resolved_path)
        # Build the inverse lookup of the mapping from tile name to tid
        tid_to_tile_name = {v: k for (k, v) in tile_name_to_tid.items()}
        # Create the 2nd mapping
        tile_name_to_pos = {}
        # Create the initial lists
        for name in tile_name_to_tid.keys():
          tile_name_to_pos[name] = []
        # Add the positions
        for (x, y, gid) in layer:
          # Ignore the empty tile
          if gid <= 0:
            continue
          pos = [x, y]
          tid = self.tiled_map.tiledgidmap[gid]
          # Append when the mapping exists
          if tid in tid_to_tile_name:
            tile_name = tid_to_tile_name[tid]
            tile_name_to_pos[tile_name].append(pos)
        tile_pos[layer.name] = tile_name_to_pos
      else:
        tile_pos[layer.name] = {}
    return tile_pos


class TiledRenderer(TiledLoader):
  # Pygame surfaces (pygame.Surface)
  screen = None
  background = None

  def __init__(self, filename):
    super().__init__(filename)

  def load(self):
    # Load the tiled map
    self.tiled_map = pytmx.util_pygame.load_pygame(self.filename)

    # Load the layers
    self.load_layers()

  def get_display_size(self):
    width = self.tiled_map.width * self.tiled_map.tilewidth
    height = self.tiled_map.height * self.tiled_map.tileheight
    return [width, height]

  def get_tile_size(self):
    return [self.tiled_map.tilewidth, self.tiled_map.tileheight]

  def get_background(self):
    """Get the background surface.

    All background layers will be blitted to the single surface.

    Returns:
      pygame.Surface: The background surface.
    """
    # Get the background layer
    background_layers = self.layers['background']
    # Create a new Pygame surface by bliting all the images on it
    background = pygame.Surface(self.screen.get_size())
    for layer in background_layers:
      for (x, y, image) in layer.tiles():
        area = [x * self.tiled_map.tilewidth, y * self.tiled_map.tileheight]
        background.blit(image, area)
    return background

  def get_overlays(self):
    """Get the overlay sprites.

    A sprite mapping file is associated with each overlay layer containing the
    sprite positions. If the property "sprite" exists, with the value of the
    file path relative to the map path, the contents of the mapping from sprite
    name to position will be read; Otherwise, an error will be raised.

    Returns:
      dict: A mapping from the name to the sprite.
    """
    # Get the tile dimension
    tile_dim = [self.tiled_map.tilewidth, self.tiled_map.tileheight]
    # Get the overlay layer
    overlay_layers = self.layers['overlay']
    # Get all the overlay images
    overlays = {}
    for layer in overlay_layers:
      # Add the overlay images
      if 'sprite' in layer.properties:
        # Build the table by pointing the position to the image
        pos_to_image = {}
        for (x, y, image) in layer.tiles():
          pos_to_image[(x, y)] = image
        # Get the sprite file path relative to the map file
        path = layer.properties['sprite']
        resolved_path = file_util.resolve_path(self.filename, path)
        # Read the sprite file
        sprite = file_util.read_yaml(resolved_path)
        # Map the name to the sprite
        for (name, pos) in sprite.items():
          x = pos['x']
          y = pos['y']
          pos = (x, y)
          if pos not in pos_to_image:
            raise KeyError(
                '{} ({}, {}) is not found in the layer'.format(name, x, y))
          # Get the image
          image = pos_to_image[pos]
          # Create a new sprite
          sprite = OverlaySprite(image, pos, tile_dim)
          # Save the sprite in the overlays
          if name in overlays:
            raise RuntimeError(
                'Duplicate name {} in the sprite file'.format(name))
          overlays[name] = sprite
      else:
        raise KeyError('"sprite" property in required for the layer {} to'
                       ' load the overlays'
                       .format(layer.name))
    return overlays

  def get_screenshot_dim(self):
    dim_2d = self.screen.get_size()
    return [dim_2d[1], dim_2d[0], 3]

  def get_screenshot(self):
    """Get the full screenshot.

    "screen" surface must be rendered first, otherwise the image will be all
    black.

    Returns:
      numpy.ndarray: The full screenshot.
    """
    # Get the entire image
    image = pygame.surfarray.pixels3d(self.screen)
    # Swap the axes as the X and Y axes in Pygame and Scipy are opposite
    image_rotated = np.swapaxes(image, 0, 1)
    # Copy the array, otherwise the surface will be locked
    return np.array(image_rotated)

  def get_po_screenshot(self, pos, radius):
    """Get the partially observable (po) screenshot.

    The returned screenshot is always a square with the length of "tile size" *
    (2 * radius + 1). The image of the agent is always centered. The default
    background is black is the cropped image is near the boundaries.

    Args:
      pos (numpy.array): The position of the partially observable area.
      radius (int): The radius of the partially observable area.

    Returns:
      numpy.ndarray: The partially observable screenshot.
    """
    # Get the entire image
    image = pygame.surfarray.pixels3d(self.screen)
    # Get the size of a single tile as a Numpy array
    tile_size = np.array(self.get_tile_size())
    # Get the size of the display
    display_size = self.get_display_size()
    # Calculate the length of the tiles needed
    tile_len = 2 * radius + 1
    # Calculate the size of the partially observable screenshot
    po_size = tile_size * tile_len
    # Calculate the offset of the crop area
    crop_offset = tile_size * (pos - radius)
    # Calculate the crop slice ((x, x+w), (y, y+h))
    crop_slice = (
        slice(np.max([0, crop_offset[0]]),
              np.min([display_size[0], crop_offset[0] + po_size[0]])),
        slice(np.max([0, crop_offset[1]]),
              np.min([display_size[1], crop_offset[1] + po_size[1]])),
    )
    # Create a black filled partially observable screenshot
    po_screenshot = np.zeros(
        (po_size[0], po_size[1], 3), dtype=image.dtype)
    # Calculate the crop size
    crop_size = [
        crop_slice[0].stop - crop_slice[0].start,
        crop_slice[1].stop - crop_slice[1].start,
    ]
    # Calculate the offset of the paste area
    paste_offset = [
        np.max([0, (-crop_offset[0])]),
        np.max([0, (-crop_offset[1])]),
    ]
    # Calculate the paste slice ((x, x+w), (y, y+h))
    paste_slice = (
        slice(paste_offset[0], paste_offset[0] + crop_size[0]),
        slice(paste_offset[1], paste_offset[1] + crop_size[1]),
    )
    # Copy and paste the partial screenshot
    po_screenshot[paste_slice] = image[crop_slice]
    # Swap the axes as the X and Y axes in Pygame and Scipy are opposite
    return np.swapaxes(po_screenshot, 0, 1)


class OverlaySprite(pygame.sprite.Sprite):
  # Position on the grid
  pos = None

  # Tile dimension
  tile_dim = None

  # Image (pygame.Surface)
  image = None

  # Image position (pygame.Rect)
  rect = None

  def __init__(self, image, pos, tile_dim):
    super().__init__()
    # Save the arguments
    self.image = image
    self.pos = pos
    self.tile_dim = tile_dim
    # Cache the Pygame Rect
    self.rect = self.image.get_rect()
    # Update the image position
    self.set_pos(self.pos)

  def get_pos(self):
    return self.pos

  def set_pos(self, pos):
    # Set the intrinsic position
    self.pos = pos
    # Set the image position
    self.rect.x = pos[0] * self.tile_dim[0]
    self.rect.y = pos[1] * self.tile_dim[1]
