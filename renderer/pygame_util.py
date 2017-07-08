# Native modules
import os

# Third-party modules
from pytmx.util_pygame import load_pygame
import pygame

# User-defined modules
from renderer.file_util import read_yaml


class TiledRenderer(object):
  # Map filename
  filename = None

  # Map
  tiled_map = None

  # Layers in the map
  layers = None

  # Pygame surfaces (pygame.Surface)
  screen = None
  background = None

  def __init__(self, filename):
    self.filename = filename

  def load(self):
    # Load the tiled map
    self.tiled_map = load_pygame(self.filename)

    # Load the layers
    self.layers = self._get_layers()

  def get_display_size(self):
    width = self.tiled_map.width * self.tiled_map.tilewidth
    height = self.tiled_map.height * self.tiled_map.tileheight
    return (width, height)

  def get_background(self):
    # Get the background layer
    background_layers = self.layers['background']
    # Create a new Pygame surface by bliting all the images
    background = pygame.Surface(self.screen.get_size())
    for layer in background_layers:
      for (x, y, image) in layer.tiles():
        area = (x * self.tiled_map.tilewidth, y * self.tiled_map.tileheight)
        background.blit(image, area)
    return background

  def get_overlays(self):
    # Get the tile dimension
    tile_dim = (self.tiled_map.tilewidth, self.tiled_map.tileheight)
    # Get the overlay layer
    overlay_layers = self.layers['overlay']
    # Get all the overlay images
    overlays = {}
    for layer in overlay_layers:
      # Build the table by pointing the position to the image
      pos_to_image = {}
      for (x, y, image) in layer.tiles():
        pos_to_image[(x, y)] = image
      # Add the overlay images
      prop = layer.properties
      if 'block' in prop:
        path = prop['block']
        resolved_path = self._get_config_path(path)
        block = read_yaml(resolved_path)
        for (name, pos) in block.items():
          x = pos['x']
          y = pos['y']
          pos = (x, y)
          if pos not in pos_to_image:
            raise ValueError(
                '{} ({}, {}) is not found in the layer'.format(name, x, y))
          # Get the image
          image = pos_to_image[pos]
          # Create a new sprite
          sprite = OverlaySprite(image, pos, tile_dim)
          # Save the sprite in the overlays
          overlays[name] = sprite
      else:
        raise ValueError(
            '"block" property in required for the layer {} to load the overlays'
            .format(layer.name))
    return overlays

  def _get_layers(self):
    layers = {
        'background': [],
        'overlay': [],
    }
    # If the custom property 'background' is true, treat the layer as
    # background
    for layer in self.tiled_map.visible_layers:
      prop = layer.properties
      if 'background' in prop and prop['background']:
        layers['background'].append(layer)
      else:
        layers['overlay'].append(layer)
    return layers

  def _get_config_path(self, path):
    # Get the directory of the map file
    map_dir = os.path.dirname(self.filename)
    # Join the path with the directory
    return os.path.join(map_dir, path)


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
