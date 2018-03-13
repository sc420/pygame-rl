# User-defined modules
import pygame_rl.renderer.pygame_renderer as pygame_renderer


class GridworldMapData:
    """Map data as the geographical info.
    """
    # Tile positions
    tile_pos = None

    def __init__(self, map_path):
        # Create a tile data and load
        tiled_data = pygame_renderer.TiledData(map_path)
        tiled_data.load()
        # Get the background tile positions
        self.tile_pos = tiled_data.get_tile_positions()
