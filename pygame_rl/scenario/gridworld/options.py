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
    # Callback to step
    step_callback = None
    # Callback to reset state
    reset_callback = None
    # Group names
    group_names = []
    # Group sizes
    group_sizes = []

    def __init__(self, map_path=None, action_space=None,
                 step_callback=None, reset_callback=None):
        self._init_map_path(map_path)
        self._init_action_space(action_space)
        self._init_step_callback(step_callback)
        self._init_reset_callback(reset_callback)
        self._init_default_group()

    def set_group(self, group_names, group_sizes):
        if len(group_names) != len(group_sizes):
            raise ValueError('Length of group names and sizes should be the '
                             'same')
        self.group_names = group_names
        self.group_sizes = group_sizes

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

    def _init_default_group(self):
        self.group_names = [
            'PLAYER1',
            'PLAYER2',
            'PLAYER3',
            'GOAL',
            'OBSTACLE1',
            'OBSTACLE2',
        ]
        self.group_sizes = [
            1,
            1,
            1,
            3,
            5,
            1,
        ]

    def _init_step_callback(self, step_callback):
        def default_callback(prev_state, action, random_state):
            del random_state
            state = copy.deepcopy(prev_state)
            # Get player 1 position
            pos = prev_state['PLAYER1'][0]
            # Get new position
            new_pos = get_new_pos(pos, action)
            # Update state
            if is_valid_pos(new_pos, prev_state):
                state['PLAYER1'][0] = new_pos
            done = is_done(pos, state)
            reward = 1.0 if done else 0.0
            info = {}
            return state, reward, done, info

        def get_new_pos(pos, action):
            new_pos = np.array(pos)
            if action == 0:  # Move right
                new_pos[0] += 1
            elif action == 1:  # Move up
                new_pos[1] -= 1
            elif action == 2:  # Move left
                new_pos[0] -= 1
            elif action == 3:  # Move down
                new_pos[1] += 1
            elif action == 4:  # Stand still
                pass
            else:
                raise ValueError('Unknown action: {}'.format(action))
            return new_pos

        def is_valid_pos(pos, prev_state):
            in_bound = (pos[0] >= 0 and pos[0] < 9 and
                        pos[1] >= 0 and pos[1] < 9)
            collision_group_names = [
                'PLAYER2',
                'PLAYER3',
                'OBSTACLE1',
                'OBSTACLE2',
            ]
            no_collision = not check_collision(
                pos, collision_group_names, prev_state)
            return in_bound and no_collision

        def is_done(pos, state):
            collision_group_names = [
                'GOAL',
            ]
            return check_collision(pos, collision_group_names, state)

        def check_collision(pos, collision_group_names, state):
            for group_index, group_name in enumerate(self.group_names):
                if not group_name in collision_group_names:
                    continue
                for local_index in range(self.group_sizes[group_index]):
                    other_pos = state[group_name][local_index]
                    if np.array_equal(pos, other_pos):
                        return True
            return False

        if step_callback:
            self.step_callback = step_callback
        else:
            self.step_callback = default_callback

    def _init_reset_callback(self, reset_callback):
        def default_callback(random_state):
            del random_state
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
