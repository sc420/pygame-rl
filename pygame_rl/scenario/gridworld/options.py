# Native modules
import copy

# Third-party modules
import gym
import numpy as np

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
    # Callback to step
    step_callback = None
    # Callback to reset state
    reset_callback = None

    def __init__(self, map_path=None, action_space=None,
                 sprite_group_names=None, sprite_group_sizes=None,
                 step_callback=None, reset_callback=None):
        self._init_map_path(map_path)
        self._init_action_space(action_space)
        self._init_sprite_group(sprite_group_names, sprite_group_sizes)
        self._init_step_callback(step_callback)
        self._init_reset_callback(reset_callback)

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

    def _init_step_callback(self, step_callback):
        def default_callback(prev_state):
            state = copy.deepcopy(prev_state)
            reward = 0.0
            done = False
            info = {}
            return state, reward, done, info

        if step_callback:
            self.step_callback = step_callback
        else:
            self.step_callback = default_callback

    def _init_reset_callback(self, reset_callback):
        def default_callback():
            return {
                'PLAYER1': np.asarray([
                    np.array([0, 0]),
                ]),
                'PLAYER2': np.asarray([
                    np.array([8, 0]),
                ]),
                'PLAYER3': np.asarray([
                    np.array([0, 8]),
                ]),
                'GOAL': np.asarray([
                    np.array([8, 4]),
                    np.array([4, 8]),
                    np.array([8, 8]),
                ]),
                'OBSTACLE1': np.asarray([
                    np.array([4, 3]),
                    np.array([3, 4]),
                    np.array([4, 4]),
                    np.array([5, 4]),
                    np.array([4, 5]),
                ]),
                'OBSTACLE2': np.asarray([
                    np.array([4, 4]),
                ]),
            }

        if reset_callback:
            self.reset_callback = reset_callback
        else:
            self.reset_callback = default_callback
