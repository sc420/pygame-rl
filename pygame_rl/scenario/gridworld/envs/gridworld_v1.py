# Third-party modules
import gym
import numpy as np

# User-defined modules
import pygame_rl.scenario.gridworld.map_data as map_data
import pygame_rl.scenario.gridworld.options as options
import pygame_rl.scenario.gridworld.renderer as renderer


class GridworldV1(gym.Env):
    """Generic gridworld Gym environment.

    The states (observation) returned by step(), reset(), render() are RGB
    arrays.
    """
    ############################################################################
    # Gym Attributes
    ############################################################################
    # Metadata
    metadata = {'render.modes': ['rgb_array']}
    # Observation space
    observation_space = None
    # Action space
    action_space = None

    ############################################################################
    # Environment Attributes
    ############################################################################
    # Environment options
    env_options = None
    # Renderer options
    renderer_options = None
    # Map data
    map_data = None
    # Renderer
    renderer = None

    ############################################################################
    # State
    ############################################################################
    # State. A dict where the key is the group name and the value is the
    # list of positions of each object.
    state = None
    # Numpy random state
    random_state = None

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

    ############################################################################
    # Gym Methods
    ############################################################################

    def seed(self, seed=None):
        self.random_state = np.random.RandomState(seed)
        return self.random_state

    def step(self, action):
        next_state, reward, done, info = self.env_options.step_callback(
            self.state, action, random_state=self.random_state)
        self.state = next_state
        obs = self._get_obs()
        return obs, reward, done, info

    def reset(self):
        # Initialize object indexes
        self._init_object_indexes()
        # Reset the state
        self.state = self.env_options.reset_callback(
            random_state=self.random_state)
        # Reset the renderer
        self.renderer.reset()
        # Return initial observation
        return self._get_obs()

    def render(self, mode='rgb_array'):
        # Render
        self.renderer.render()
        # Return renderer sceenshot
        return self.renderer.get_screenshot()

    ############################################################################
    # Initialization Methods
    ############################################################################

    def load(self):
        # Save or create environment options
        self.env_options = self.env_options or options.GridworldOptions()
        # Load map data
        self.map_data = map_data.GridworldMapData(self.env_options.map_path)
        # Initialize renderer
        self.renderer = renderer.GridworldRenderer(
            self.env_options.map_path, self, self.renderer_options)
        # Load the renderer
        self.renderer.load()
        # Initialize observation space
        self._init_obs_space()
        # Initialize action space
        self.action_space = self.env_options.action_sapce

    def _init_object_indexes(self):
        self.object_indexes = {}
        global_index = 0
        # Iterate each group
        for group_index, group_name in enumerate(self.env_options.group_names):
            group_indexes = {}
            group_size = self.env_options.group_sizes[group_index]
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
        display_size = self.renderer.get_display_size()
        nvec = [display_size[0], display_size[1], 3]
        self.observation_space = gym.spaces.MultiDiscrete(nvec)

    ############################################################################
    # Observation Retrieval
    ############################################################################

    def _get_obs(self):
        # Render
        self.renderer.render()
        # Return renderer sceenshot
        return self.renderer.get_screenshot()


def index_2d_to_1d(pos, width):
    px, py = pos
    return np.asscalar((width * py) + px)
