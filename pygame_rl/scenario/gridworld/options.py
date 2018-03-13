# Third-party modules
import gym

# User-defined modules
import pygame_rl.util.file_util as file_util


class GridworldOptions:
    """Environment options.
    """
    # Internal map resource name
    map_resource_name = 'pygame_rl/data/map/gridworld/gridworld.tmx'
    # Map path
    map_path = None
    # Action space
    action_sapce = None
    # Sprite group names
    sprite_group_names = None
    # Sprite group sizes
    sprite_group_sizes = None
    # Callback to update overlays
    update_overlay_callback = None

    def __init__(self, map_path=None, action_space=None,
                 sprite_group_names=None, sprite_group_sizes=None,
                 update_overlay_callback=None):
        self._init_map_path(map_path)
        self._init_action_space(action_space)
        self._init_sprite_group(sprite_group_names, sprite_group_sizes)
        self.update_overlay_callback = update_overlay_callback

    def _init_map_path(self, map_path):
        if map_path:
            self.map_path = map_path
        else:
            self.map_path = file_util.get_resource_path(self.map_resource_name)

    def _init_action_space(self, action_space):
        if action_space:
            self.action_sapce = action_space
        else:
            # 4-directional walk and stand still
            self.action_sapce = gym.spaces.Discrete(5)

    def _init_sprite_group(self, sprite_group_names, sprite_group_sizes):
        if sprite_group_names and sprite_group_sizes:
            if len(self.sprite_group_names) != len(self.sprite_group_sizes):
                raise ValueError('Length of group names and sizes should be the'
                                 'same')
            self.sprite_group_names = sprite_group_names
            self.sprite_group_sizes = sprite_group_sizes
        else:
            # Set default group names and sizes in internal map
            self.sprite_group_names = [
                'PLAYER1',
                'PLAYER2',
                'PLAYER3',
                'GOAL',
                'OBSTACLE1',
                'OBSTACLE2',
            ]
            self.sprite_group_sizes = [
                1,
                1,
                1,
                3,
                5,
                1,
            ]
