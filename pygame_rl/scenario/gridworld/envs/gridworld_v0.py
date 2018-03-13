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

    ############################################################################
    # State
    ############################################################################
    # Timestamp
    timestamp = 0
    # State. A dict where the key is the group name and the value is the
    # list of positions of each object.
    state = None

    ############################################################################
    # Cached Objects
    ############################################################################
    # Object indexes. A dict where the key is the group name and the value is
    # the 2nd dict, where the key is the local index and the key is the global
    # index.
    object_indexes = {}
    # Reverse object indexes. A reverse lookup dict of 'object_indexes'. A dict
    # where the key is the global index and the value is [group name,
    # local object index].
    reverse_object_indexes = {}
    # Total object numbers
    total_object_num = 0

    def __init__(self, env_options=None, renderer_options=None):
        # Save or create environment options
        self.options = env_options or options.GridworldOptions()
        # Initialize object indexes
        self._init_object_indexes()
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
        return self.options.step_callback(self.state)

    def reset(self):
        self.state = self.options.reset_callback()
        return self._get_obs()

    def render(self, mode='human'):
        pass

    ############################################################################
    # Initialization Methods
    ############################################################################

    def _init_object_indexes(self):
        self.object_indexes = {}
        global_index = 0
        # Iterate each group
        for group_index, group_name in enumerate(
                self.options.sprite_group_names):
            group_indexes = {}
            group_size = self.options.sprite_group_sizes[group_index]
            # Iterate each local object
            for local_index in range(group_size):
                group_indexes[local_index] = global_index
                self.reverse_object_indexes[global_index] = [
                    group_name, local_index]
                global_index += 1
            self.object_indexes[group_name] = group_indexes
        # Save the total object number
        self.total_object_num = global_index

    def _init_obs_space(self):
        map_size = self.renderer.get_map_size()
        flattened_map_size = map_size.prod()
        nvec = np.repeat(self.total_object_num, flattened_map_size)
        self.observation_space = gym.spaces.MultiDiscrete(nvec)

    ############################################################################
    # Observation Retrieval
    ############################################################################

    def _get_obs(self):
        """Get flattened observation.

        The observation is a flattened vector of one-hot vectors, the flattened
        (row-major) vector is the representation of the 2D map, and each one-hot
        vector represents existence of the objects, with each index the global
        index of the object.
        """
        map_size = self.renderer.get_map_size()
        map_width = map_size[1]
        flattened_map_size = map_size.prod()
        obs = np.zeros(
            [flattened_map_size, self.total_object_num], dtype=np.int)
        for group_name, positions in self.state.items():
            for local_index, pos in enumerate(positions):
                index_1d = index_2d_to_1d(pos, map_width)
                global_index = self.object_indexes[group_name][local_index]
                obs[index_1d][global_index] = 1
        return obs


def index_2d_to_1d(pos, width):
    px, py = pos
    return np.asscalar((width * py) + px)
