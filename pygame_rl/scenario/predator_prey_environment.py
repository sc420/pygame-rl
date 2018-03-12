# Native modules
import copy
import math
import random

# Third-party modules
import numpy as np
import pypaths.astar as astar

# User-defined modules
import pygame_rl.renderer.pygame_renderer as pygame_renderer
import pygame_rl.rl.environment as environment
import pygame_rl.scenario.predator_prey_renderer as predator_prey_renderer
import pygame_rl.util.file_util as file_util


class PredatorPreyEnvironment(environment.Environment):
    """The predator-prey environment.
    """
    # Group names
    group_names = [
        'PREDATOR',
        'PREY',
        'OBSTACLE',
    ]

    # Action list
    actions = [
        'MOVE_RIGHT',
        'MOVE_UP',
        'MOVE_LEFT',
        'MOVE_DOWN',
        'STAND',
    ]

    # Action indexes
    action_indexes = None

    # Action weight
    action_weight = [
        0.2,
        0.3,
        0.2,
        0.3,
        0.0,
    ]

    # Pathfinder cost weight
    pathfinder_cost_weight = {
        'MOVE_RIGHT': 0.3,
        'MOVE_UP': 0.2,
        'MOVE_LEFT': 0.3,
        'MOVE_DOWN': 0.2,
        'STAND': 0.0,
    }

    # Noise (Gaussian: mean and standard deviation)
    gauss_noise = [0.0, 0.01]

    # Environment options
    options = None

    # State
    state = None

    # Map data
    map_data = None

    # Renderer
    renderer = None
    renderer_loaded = False

    # Object index range
    object_index_range = None

    # Cached action map
    cached_action = None

    # Cached reward
    cached_reward = None

    def __init__(self, env_options=None, renderer_options=None):
        # Save or create environment options
        self.options = env_options or PredatorPreyEnvironmentOptions()
        # Calculate action indexes
        self._calc_action_indexes()
        # Calculate object index ranges
        self._calc_group_index_ranges()
        # Load map data
        self.map_data = PredatorPreyMapData(self.options.map_path)
        # Initialize the state
        self.state = PredatorPreyState(self, self.options, self.map_data)
        # Initialize the renderer
        self.renderer = predator_prey_renderer.PredatorPreyRenderer(
            self.options.map_path, self, renderer_options)
        # Initialize cached action map
        self._init_cached_action()

    def get_group_index_range(self, group_name):
        return self.object_index_range[group_name]

    def get_group_name(self, object_index):
        if object_index is None:
            return None
        for (group_name, index_range) in self.object_index_range.items():
            if object_index >= index_range[0] and object_index < index_range[1]:
                return group_name
        return None

    def reset(self):
        self.state.reset()
        return PredatorPreyObservation(self.state, None, 0.0, None)

    def step(self, actions):
        """Step with actions and return an observation.

        Args:
            actions (list): A list of actions of all objects.

        Returns:
            PredatorPreyObservation: Observation.
        """
        # Check the action size
        if len(actions) != self.options.get_total_object_size():
            raise ValueError('Action size should be equal to the object size')
        # Set cached actions
        for object_index, action in enumerate(actions):
            self.cached_action[object_index] = action
        # Update the state and return the observation
        return self.update_state()

    def step_without_obstacles(self, actions_wo):
        """Step with actions and return an observation, but without actions of
        obstacles.

        Args:
            actions_wo (list): A list of actions of predators and preys.

        Returns:
            PredatorPreyObservation: Observation.
        """
        # Prepare the actions
        actions = [None] * self.options.get_total_object_size()
        # Get the object sizes and index ranges
        predator_size = self.options.object_size['PREDATOR']
        prey_size = self.options.object_size['PREY']
        predator_index_range = self.get_group_index_range('PREDATOR')
        prey_index_range = self.get_group_index_range('PREY')
        # Fill in the actions
        actions[:predator_size] = actions_wo[slice(*predator_index_range)]
        actions[-prey_size:] = actions_wo[slice(*prey_index_range)]
        # Use the filled actions to call the step function
        return self.step(actions)

    def take_action(self, action):
        """Take actions at once and return an observation.

        Args:
            actions (dict): A dict of actions in which keys are object indexes
                and values are actions.

        Returns:
            PredatorPreyObservation: Observation.
        """
        self.cached_action = action
        return self.update_state()

    def take_cached_action(self, object_index, action):
        """Take a cached action.

        It's useful when giving a single action one by one.

        Args:
            object_index (int): The object index.
            action (string): The intended action.
        """
        self.cached_action[object_index] = action

    def update_state(self):
        # Update agent actions
        self._update_agent_actions()
        # Update agent positions
        self._update_agent_pos()
        # Update taken actions
        self._update_taken_actions()
        # Update frame skipping index
        self._update_frame_skip_index()
        # Update time step
        self._update_time_step()
        # Get the reward
        reward = self._get_reward()
        # Create the observation
        observation = PredatorPreyObservation(
            None, self.cached_action, reward, self.state)
        # Reset cached action map
        self._init_cached_action()
        # Return the observation
        return observation

    def render(self):
        # Lazy load the renderer
        if not self.renderer_loaded:
            self.renderer.load()
            self.renderer_loaded = True
        # Render
        self.renderer.render()

    def _init_cached_action(self):
        self.cached_action = {}
        for object_index in range(self.options.get_total_object_size()):
            self.cached_action[object_index] = None

    def _calc_action_indexes(self):
        self.action_indexes = {}
        for index, action in enumerate(self.actions):
            self.action_indexes[action] = index

    def _calc_group_index_ranges(self):
        # Initialize the range
        self.object_index_range = {}
        # Calculate start and end indexes for each group and increment the start
        # index
        start_index = 0
        for group_name in self.group_names:
            end_index = start_index + self.options.object_size[group_name]
            self.object_index_range[group_name] = [start_index, end_index]
            start_index = end_index

    def _update_agent_actions(self):
        for object_index in range(self.options.get_total_object_size()):
            # Skip if the prey is not available
            if not self.state.get_object_availability(object_index):
                continue
            # Skip if the cached action has been specified
            if self.cached_action[object_index]:
                continue
            # Select the previous action if it's frame skipping; otherwise, use
            # rule-based action
            if self.state.get_object_frame_skip_index(object_index) > 0:
                action = self.state.get_object_action(object_index)
            else:
                action = self._get_agent_ai_action(object_index)
            # Update the cached action
            self.cached_action[object_index] = action

    def _update_agent_pos(self):
        intended_pos = self._get_intended_pos()
        to_continue = True
        # Avoid overlapping positions
        while to_continue:
            to_continue = False
            overlapping_pos = self._get_overlapping_pos(intended_pos)
            for _, object_index_list in overlapping_pos.items():
                # Resolve overlapping
                if len(object_index_list) > 1:
                    # Check whether to update prey availabilities
                    if self._is_overlapping_allowed(object_index_list):
                        self._update_prey_availabilities(object_index_list)
                    # Restore the position
                    for object_index in object_index_list:
                        intended_pos[object_index] = self.state.get_object_pos(
                            object_index)
                    to_continue = True
        for object_index, pos in enumerate(intended_pos):
            self.state.set_object_pos(object_index, pos)

    def _update_prey_availabilities(self, overlapping_object_index_list):
        # Reset cached reward
        self.cached_reward = 0.0
        # Check overlapping positions
        for object_index in overlapping_object_index_list:
            if self.get_group_name(object_index) == 'PREY':
                self.state.set_object_availability(object_index, False)
                self.cached_reward += 1.0

    def _update_taken_actions(self):
        for object_index in range(self.options.get_total_object_size()):
            action = self.cached_action[object_index]
            action = action or 'STAND'
            self.state.set_object_action(object_index, action)

    def _update_frame_skip_index(self):
        for object_index in range(self.options.get_total_object_size()):
            self.state.increase_frame_skip_index(
                object_index, self.options.ai_frame_skip)

    def _update_time_step(self):
        self.state.increase_time_step()

    def _add_weighted_predator_actions(self, predator_pos, prey_pos,
                                       weighted_actions):
        # Only when the distance is within the partially observable range
        if not self._is_distance_in_po(predator_pos, prey_pos):
            return
        finder = astar.pathfinder(distance=astar.absolute_distance,
                                  cost=self._pathfinder_weighted_cost(),
                                  neighbors=self._pathfinder_grid_neighbors())
        # Find the shortest path
        cost, path = finder(tuple(predator_pos), tuple(prey_pos))
        # Get the next position in the path
        if len(path) > 1:
            next_pos = path[1]
        else:
            next_pos = path[0]
        # Get the action that leads to the next position
        action_index = self._get_pos_action(predator_pos, next_pos)
        # Add the weighted action
        weighted_actions[action_index] += 1 / (cost + 1)

    def _add_weighted_prey_actions(self, prey_pos, predator_pos,
                                   weighted_actions):
        # Only when the distance is within the partially observable range
        if not self._is_distance_in_po(prey_pos, predator_pos):
            return
        # Get distances to move away
        distances = self._get_moved_away_distances(prey_pos, predator_pos)
        # Choose the farthest distance
        action_index = np.argmax(distances)
        # Get the farthest distance
        distance = distances[action_index]
        # Get the action weight
        weight = self.action_weight[action_index]
        # Add the weighted action
        weighted_actions[action_index] += weight / distance

    def _is_overlapping_allowed(self, object_index_list):
        # Get the group names
        group_name_list = [self.get_group_name(object_index)
                           for object_index in object_index_list]
        # Count the group names
        predator_count = group_name_list.count('PREDATOR')
        prey_count = group_name_list.count('PREY')
        # Allow when there are more than 1 predators and at least 1 prey
        return predator_count >= 2 and prey_count >= 1

    def _is_distance_in_po(self, pos1, pos2):
        distance = get_pos_distance(pos1, pos2)
        po_distance = self.options.po_radius
        return distance <= po_distance

    def _get_agent_ai_action(self, object_index):
        group_name = self.get_group_name(object_index)
        if group_name == 'PREDATOR':
            return self._get_predator_ai_action(object_index)
        elif group_name == 'PREY':
            return self._get_prey_ai_action(object_index)

    def _get_predator_ai_action(self, predator_object_index):
        # Get predator position
        predator_pos = self.state.get_object_pos(predator_object_index)
        # Get index ranges
        prey_index_range = self.get_group_index_range('PREY')
        # Calculate weighted actions
        weighted_actions = [0.0 for _ in self.actions]
        for prey_object_index in range(*prey_index_range):
            # Skip unavailable prey
            if not self.state.get_object_availability(prey_object_index):
                continue
            # Get prey position
            prey_pos = self.state.get_object_pos(prey_object_index)
            # Add weighted actions
            self._add_weighted_predator_actions(
                predator_pos, prey_pos, weighted_actions)
        # Add noises to the weighted actions
        weighted_actions = self._get_noised_values(weighted_actions)
        # Pick the max weighted action
        action_index = np.argmax(weighted_actions)
        return self.actions[action_index]

    def _get_prey_ai_action(self, prey_object_index):
        # Get prey position
        prey_pos = self.state.get_object_pos(prey_object_index)
        # Get index ranges
        predator_index_range = self.get_group_index_range('PREDATOR')
        # Calculate weighted actions
        weighted_actions = [0.0 for _ in self.actions]
        for predator_object_index in range(*predator_index_range):
            # Get predator position
            predator_pos = self.state.get_object_pos(predator_object_index)
            # Add weighted actions
            self._add_weighted_prey_actions(
                prey_pos, predator_pos, weighted_actions)
        # Add noises to the weighted actions
        weighted_actions = self._get_noised_values(weighted_actions)
        # Pick the max weighted action
        agent_index = np.argmax(weighted_actions)
        return self.actions[agent_index]

    def _get_intended_pos(self):
        intended_pos = [None for _ in range(
            self.options.get_total_object_size())]
        for object_index in range(self.options.get_total_object_size()):
            pos = self.state.get_object_pos(object_index)
            action = self.cached_action[object_index]
            # Use the previous action if it's not specified
            if not action:
                action = self.state.get_object_action(object_index)
            # Get the moved position
            moved_pos = self._get_moved_pos(pos, action)
            # Check whether the position is valid
            if moved_pos in self.map_data.field:
                intended_pos[object_index] = moved_pos
            else:
                intended_pos[object_index] = pos
        return intended_pos

    def _get_overlapping_pos(self, pos_list):
        overlapping_pos = {}
        for object_index, pos in enumerate(pos_list):
            # Skip unavailable object
            if not self.state.get_object_availability(object_index):
                continue
            # Use the tuple as the key
            pos_tuple = tuple(pos)
            if pos_tuple in overlapping_pos:
                overlapping_pos[pos_tuple].append(object_index)
            else:
                overlapping_pos[pos_tuple] = [object_index]
        return overlapping_pos

    def _get_reward(self):
        return self.cached_reward

    def _get_moved_away_distances(self, pos_move, pos_ref):
        # Prepare the list
        moved_pos_list = [None for _ in self.actions]
        # Fill in the list with each action
        for action_index, action in enumerate(self.actions):
            # Get the position after the move
            moved_pos = self._get_moved_pos(pos_move, action)
            # Check whether the position has been occupied
            no_overlap = self.state.get_pos_status(moved_pos) is None
            # Check whether the position is in the field
            in_field = moved_pos in self.map_data.field
            # Choose the moved position when the 2 conditions are both true;
            # otherwise, use the original position
            if no_overlap and in_field:
                moved_pos_list[action_index] = moved_pos
            else:
                moved_pos_list[action_index] = pos_move
        # Calculate distances for each moved position
        distances = [get_pos_distance(moved_pos, pos_ref)
                     for moved_pos in moved_pos_list]
        return distances

    def _pathfinder_weighted_cost(self):
        def func(c1, c2):
            vec_x = c1[0] - c2[0]
            vec_y = c1[1] - c2[1]
            if vec_x > 0:
                weight_x = self.pathfinder_cost_weight['MOVE_RIGHT']
            elif vec_x < 0:
                weight_x = self.pathfinder_cost_weight['MOVE_LEFT']
            else:
                weight_x = self.pathfinder_cost_weight['STAND']
            if vec_y > 0:
                weight_y = self.pathfinder_cost_weight['MOVE_DOWN']
            elif vec_y < 0:
                weight_y = self.pathfinder_cost_weight['MOVE_UP']
            else:
                weight_y = self.pathfinder_cost_weight['STAND']
            return weight_x * abs(vec_x) + weight_y * abs(vec_y)
        return func

    def _pathfinder_grid_neighbors(self):
        def func(coord):
            neighbor_list = [(coord[0], coord[1] + 1),
                             (coord[0], coord[1] - 1),
                             (coord[0] + 1, coord[1]),
                             (coord[0] - 1, coord[1])]
            return [c for c in neighbor_list
                    if list(c) in self.map_data.field
                    and self.get_group_name(self.state.get_pos_status(c)) !=
                    'OBSTACLE']
        return func

    def _get_moved_pos(self, pos, action):
        # Copy the position
        moved_pos = list(pos)
        # Move to 4-direction grid point
        if action == 'MOVE_RIGHT':
            moved_pos[0] += 1
        elif action == 'MOVE_UP':
            moved_pos[1] -= 1
        elif action == 'MOVE_LEFT':
            moved_pos[0] -= 1
        elif action == 'MOVE_DOWN':
            moved_pos[1] += 1
        elif action == 'STAND':
            pass
        else:
            raise KeyError('Unknown action {}'.format(action))
        return moved_pos

    def _get_pos_action(self, pos1, pos2):
        if pos1 == pos2:
            return self.action_indexes['STAND']
        else:
            if pos1[0] == pos2[0]:
                if pos1[1] < pos2[1]:
                    return self.action_indexes['MOVE_DOWN']
                else:
                    return self.action_indexes['MOVE_UP']
            elif pos1[1] == pos2[1]:
                if pos1[0] < pos2[0]:
                    return self.action_indexes['MOVE_RIGHT']
                else:
                    return self.action_indexes['MOVE_LEFT']
            else:
                raise ValueError('Expect two positions to be adjacent')

    def _get_noised_values(self, values):
        return [value + random.gauss(*self.gauss_noise) for value in values]


class PredatorPreyEnvironmentOptions(object):
    """The options for predator-prey environment.
    """
    # Resource names
    map_resource_name = 'pygame_rl/data/map/predator_prey/predator_prey.tmx'

    # Map path
    map_path = None

    # Number of the objects in each group
    object_size = None

    # Partially observable radius
    po_radius = None

    # Frame skip for AI
    ai_frame_skip = None

    def __init__(self, map_path=None, object_size=None, po_radius=np.inf,
                 ai_frame_skip=1):
        # Save the map path or use the internal resource
        if map_path:
            self.map_path = map_path
        else:
            self.map_path = file_util.get_resource_path(self.map_resource_name)
        # Save the number of predators, preys and obstacles
        if object_size:
            self.object_size = object_size
        else:
            self.object_size = {
                'PREDATOR': 2,
                'PREY': 2,
                'OBSTACLE': 10,
            }
        # Save the partially observable radius
        self.po_radius = po_radius
        # Save the frame skip
        self.ai_frame_skip = ai_frame_skip
        # Calculate index ranges for each group

    def get_total_object_size(self):
        total_size = 0
        for (_, size) in self.object_size.items():
            total_size += size
        return total_size


class PredatorPreyMapData(object):
    """The map data as the geographical info.
    """
    # Tile positions
    field = []

    def __init__(self, map_path):
        # Create a tile data and load
        tiled_data = pygame_renderer.TiledData(map_path)
        tiled_data.load()
        # Get the background tile positions
        tile_pos = tiled_data.get_tile_positions()
        # Build the tile positions
        self.field = tile_pos['ground']['FIELD']


class PredatorPreyObservation(object):
    """The observation as a response by the environment.
    """
    state = None
    action = None
    reward = 0.0
    next_state = None

    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state

    def __repr__(self):
        return 'State:\n{}\nAction: {}\nReward: {}\nNext state:\n{}'.format(
            self.state, self.action, self.reward, self.next_state)


class PredatorPreyState(object):
    """The internal state.
    """
    # Object statuses as a list, each item is an object with the properties:
    # * group: Group
    # * pos: Position
    # * available: Availability
    # * action: Last taken action for the agent
    # * frame_skip_index: Current frame skipping index, starting from 0,
    # resetting after it reaches the frame skip
    object_list = None

    # Object statuses at the previous time step with only the properties:
    # * pos: Position
    prev_object_list = None

    # Position to object index map
    pos_map = None

    # Time step
    time_step = 0

    # Soccer environment
    env = None

    # Soccer environment options
    env_options = None

    # Map data
    map_data = None

    def __init__(self, env, env_options, map_data):
        self.env = env
        self.env_options = env_options
        self.map_data = map_data
        self.reset()

    def reset(self):
        # Initialize object list
        self._reset_object_list()
        # Reset position map
        self._reset_pos_map()
        # Randomize the agent statuses
        self.randomize()
        # Initialize the time step
        self.time_step = 0

    def randomize(self):
        free_pos = copy.deepcopy(self.map_data.field)
        # Shuffle the positions
        random.shuffle(free_pos)
        # Create a unused indicators
        unused = [True] * len(free_pos)
        # Randomize the position of each object in each group
        for group_name in self.env.group_names:
            index_range = self.env.get_group_index_range(group_name)
            for object_index in range(*index_range):
                # Get one of the shuffled position in the field
                found = False
                for pos_index, pos in enumerate(free_pos):
                    if (unused[pos_index] and
                            self._check_no_adjacent_object(pos)):
                        # Update the position
                        self.set_object_pos(object_index, pos)
                        # Set the unused indicator
                        unused[pos_index] = False
                        # Mark the position has been found
                        found = True
                        # Continue to the next object
                        break
                if not found:
                    raise ValueError('Unable to find free position')

    def is_terminal(self):
        # When the time step hits the limit
        if self.time_step >= 100:
            return True
        # When none of the preys is available
        prey_index_range = self.env.get_group_index_range('PREY')
        any_available = False
        for object_index in range(*prey_index_range):
            if self.get_object_availability(object_index):
                any_available = True
                break
        if not any_available:
            return True
        # Otherwise, the state isn't terminal
        return False

    def get_object_group(self, object_index):
        return self.object_list[object_index]['group']

    def set_object_group(self, object_index, group):
        self.object_list[object_index]['group'] = group

    def get_object_pos(self, object_index):
        return self.object_list[object_index]['pos']

    def set_object_pos(self, object_index, pos):
        # Get old position
        old_pos = self.object_list[object_index].get('pos', None)
        # Set previous position
        prev_pos = old_pos
        if not old_pos:
            prev_pos = pos
        self.set_prev_object_pos(object_index, prev_pos)
        # Remove old position from map
        if old_pos:
            old_pos_tuple = tuple(old_pos)
            self.pos_map.pop(old_pos_tuple, None)
        # Set position in map
        if pos:
            pos_tuple = tuple(pos)
            self.pos_map[pos_tuple] = object_index
        # Set object list
        self.object_list[object_index]['pos'] = pos

    def set_prev_object_pos(self, object_index, pos):
        self.prev_object_list[object_index]['pos'] = pos

    def get_prev_object_pos(self, object_index):
        return self.prev_object_list[object_index]['pos']

    def get_object_vel(self, object_index):
        prev_pos = self.get_prev_object_pos(object_index)
        pos = self.get_object_pos(object_index)
        vel = [
            pos[0] - prev_pos[0],
            pos[1] - prev_pos[1],
        ]
        return vel

    def get_object_availability(self, object_index):
        return self.object_list[object_index]['available']

    def set_object_availability(self, object_index, available):
        self.object_list[object_index]['available'] = available

    def get_object_action(self, object_index):
        return self.object_list[object_index]['action']

    def set_object_action(self, object_index, action):
        self.object_list[object_index]['action'] = action

    def get_object_frame_skip_index(self, object_index):
        return self.object_list[object_index]['frame_skip_index']

    def set_object_frame_skip_index(self, object_index, frame_skip_index):
        self.object_list[object_index]['frame_skip_index'] = frame_skip_index

    def increase_frame_skip_index(self, object_index, frame_skip):
        old_frame_skip_index = self.object_list[object_index][
            'frame_skip_index']
        new_frame_skip_index = (old_frame_skip_index + 1) % frame_skip
        self.object_list[object_index]['frame_skip_index'] = \
            new_frame_skip_index

    def increase_time_step(self):
        self.time_step += 1

    def get_pos_status(self, pos):
        pos_tuple = tuple(pos)
        return self.pos_map.get(pos_tuple, None)

    def get_po_symbolic_view(self, pos, radius):
        """Get partially observable (po) symbolic view.

        The returned view is always a square with the length of (2 * radius +
        1). The position is always centered. The default background is black if
        the cropped image is near the boundaries.

        Args:
            pos (Array-like): The position of partially observable area.
            radius (int): The radius of partially observable area.

        Returns:
            numpy.ndarray: Partially observable symbolic view. Each value is the
                object index beginning from 0. If there is no object, the value
                will be -1.
        """
        # Get the size of a single tile as a Numpy array
        tile_size = np.array(self.env.renderer.get_tile_size())
        # Make sure position is numpy array
        pos = np.array(pos)
        # Calculate length of the crop area
        crop_len = 2 * radius + 1
        # Calculate offset of the crop area
        crop_offset = pos - radius
        # Calculate crop range ((x, x+w), (y, y+h))
        crop_range = (
            (np.max([0, crop_offset[0]]),
             np.min([tile_size[0], crop_offset[0] + crop_len])),
            (np.max([0, crop_offset[1]]),
             np.min([tile_size[1], crop_offset[1] + crop_len])),
        )
        # Create a black filled partially observable view
        po_view = np.zeros((crop_len, crop_len), dtype=int)
        # Calculate offset of the paste area
        paste_offset = [
            np.max([0, (-crop_offset[0])]),
            np.max([0, (-crop_offset[1])]),
        ]
        # Fill in position statuses
        for x_crop in range(*crop_range[0]):
            for y_crop in range(*crop_range[1]):
                x_paste = x_crop - crop_range[0][0] + paste_offset[0]
                y_paste = y_crop - crop_range[1][0] + paste_offset[1]
                pos_crop = [x_crop, y_crop]
                pos_status = self.get_pos_status(pos_crop)
                if pos_status is None:
                    po_view[x_paste, y_paste] = -1
                else:
                    group = self.get_object_group(pos_status)
                    po_view[x_paste, y_paste] = self.env.group_names.index(
                        group)
        return po_view

    def get_symbolic_features(self):
        """Get symbolic features. The features consist of the positions,
        velocities, and availabilities.

        Returns:
            numpy.ndarray: A sequence of pairs for each object in order: [x1,
                y1, vx1, vy1, a1, ..., xn, yn, vxn, vyn, an], where (x1, y1) is
                the position, (vx1, vy1) is the velocity, and a1 is the
                availability of object 1. n is the number of objects.
        """
        total_object_size = self.env_options.get_total_object_size()
        # xi, yi, vxi, vyi, ai for object index i
        pair_size = 5
        features = np.zeros(pair_size * total_object_size)
        for object_index in range(total_object_size):
            # Get position, velocity, and availability
            pos = self.get_object_pos(object_index)
            vel = self.get_object_vel(object_index)
            availability = self.get_object_availability(object_index)
            # Fill in the feature list
            features[pair_size * object_index + 0] = pos[0]
            features[pair_size * object_index + 1] = pos[1]
            features[pair_size * object_index + 2] = vel[0]
            features[pair_size * object_index + 3] = vel[1]
            features[pair_size * object_index + 4] = availability
        return features

    def _check_no_adjacent_object(self, pos):
        total_object_size = self.env_options.get_total_object_size()
        for object_index in range(total_object_size):
            object_pos = self.get_object_pos(object_index)
            if object_pos and get_pos_distance(pos, object_pos) < 2:
                return False
        return True

    def _reset_object_list(self):
        total_object_size = self.env_options.get_total_object_size()
        # Initialize object lists
        self.object_list = [{} for _ in range(total_object_size)]
        self.prev_object_list = [{} for _ in range(total_object_size)]
        # Fill in object details
        for group_name in self.env.group_names:
            index_range = self.env.get_group_index_range(group_name)
            for object_index in range(*index_range):
                # For current time step
                self.set_object_group(object_index, group_name)
                self.set_object_pos(object_index, None)
                self.set_object_availability(object_index, True)
                self.set_object_action(object_index, 'STAND')
                self.set_object_frame_skip_index(object_index, 0)
                # For previous time step
                self.set_prev_object_pos(object_index, None)

    def _reset_pos_map(self):
        self.pos_map = {}

    def __repr__(self):
        message = ''
        # Get the object index ranges
        predator_index_range = self.env.get_group_index_range('PREDATOR')
        prey_index_range = self.env.get_group_index_range('PREY')
        # The agent positions, availabilities and actions
        first_line = True
        message += 'Predators (Position,Action):\n'
        for predator_index in range(*predator_index_range):
            if first_line:
                first_line = False
            else:
                message += '\n'
            pos = self.get_object_pos(predator_index)
            action = self.get_object_action(predator_index)
            message += '{},{}'.format(pos, action)
        first_line = True
        message += '\nPreys (Position,Availability,Action):\n'
        for prey_index in range(*prey_index_range):
            if first_line:
                first_line = False
            else:
                message += '\n'
            pos = self.get_object_pos(prey_index)
            availability = self.get_object_availability(prey_index)
            action = self.get_object_action(prey_index)
            message += '{},{},{}'.format(pos, availability, action)
        # The time step
        message += '\nTime step: {}'.format(self.time_step)
        return message


def get_pos_distance(pos1, pos2):
    return math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1])
