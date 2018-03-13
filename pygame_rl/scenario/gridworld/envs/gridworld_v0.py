# Third-party modules
import gym
import numpy as np

# User-defined modules
import pygame_rl.scenario.gridworld.map_data as map_data
import pygame_rl.scenario.gridworld.options as options
import pygame_rl.scenario.gridworld.renderer as renderer


class GridworldV0(gym.Env):
    """Generic gridworld Gym environment.
    """
    ############################################################################
    # Gym Attributes
    ############################################################################
    # Metadata
    metadata = {'render.modes': ['human', 'rgb_array']}
    # Observation space
    observation_space = None
    # Action space
    action_space = None

    ############################################################################
    # Environment Attributes
    ############################################################################
    # Environment options
    options = None
    # Map data
    map_data = None
    # Renderer
    renderer = None
    # Timestamp
    timestamp = 0

    ############################################################################
    # Cached Objects
    ############################################################################
    object_indexes = {}
    object_names = {}

    def __init__(self, env_options=None, renderer_options=None):
        # Save or create environment options
        self.options = env_options or options.GridworldOptions()
        # Initialize object indexes and names
        self._init_object_indexes_and_names()
        # Load map data
        self.map_data = map_data.GridworldMapData(self.options.map_path)
        # Initialize renderer
        self.renderer = renderer.GridworldRenderer(
            self.options.map_path, self, renderer_options)
        # Load the renderer
        self.renderer.load()
        # Initialize observation space
        self._init_obs_space()
        # Initialize action space
        self.action_space = self.options.action_sapce

    ############################################################################
    # Gym Methods
    ############################################################################

    def seed(self, seed=None):
        pass

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    ############################################################################
    # Initialization Methods
    ############################################################################

    def _init_object_indexes_and_names(self):
        self.object_indexes = {}
        global_index = 0
        for group_index, group_name in enumerate(
                self.options.sprite_group_names):
            group_indexes = {}
            group_size = self.options.sprite_group_sizes[group_index]
            for object_index in range(group_size):
                group_indexes[object_index] = global_index
                self.object_names[global_index] = [group_name, object_index]
                global_index += 1
            self.object_indexes[group_name] = group_indexes

    def _init_obs_space(self):
        map_size = self.renderer.get_map_size()
        flattened_map_size = map_size.prod()
        total_tile_num = self.renderer.get_total_tile_num()
        nvec = np.repeat(total_tile_num, flattened_map_size)
        self.observation_space = gym.spaces.MultiDiscrete(nvec)
