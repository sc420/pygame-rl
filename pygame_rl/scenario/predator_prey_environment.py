# Native modules
import collections
import copy
import random

# Third-party modules
import numpy as np

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

  # Action weight
  action_weight = [
      0.2,
      0.3,
      0.2,
      0.3,
      0.0,
  ]

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
    for (group_name, index_range) in self.object_index_range.items():
      if object_index >= index_range[0] and object_index < index_range[1]:
        return group_name
    return None

  def reset(self):
    self.state.reset()
    return PredatorPreyObservation(self.state, None, 0.0, None)

  def take_action(self, action):
    self.cached_action = action
    return self.update_state()

  def take_cached_action(self, object_index, action):
    self.cached_action[object_index] = action

  def update_state(self):
    # Update prey actions
    self._update_prey_actions()
    # Update agent positions
    self._update_agent_pos()
    # Update prey availabilities
    self._update_prey_availabilities()
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

  def _calc_group_index_ranges(self):
    self.object_index_range = {}
    start_index = 0
    for group_name in self.group_names:
      end_index = start_index + self.options.object_size[group_name]
      self.object_index_range[group_name] = [start_index, end_index]
      start_index = end_index

  def _update_prey_actions(self):
    # Get index ranges
    predator_index_range = self.get_group_index_range('PREDATOR')
    prey_index_range = self.get_group_index_range('PREY')
    # Get predator positions
    predator_pos_list = [self.state.get_object_pos(object_index)
                         for object_index in range(*predator_index_range)]
    # Calculate weighted actions
    weighted_actions = [0.0 for _ in self.actions]
    for prey_object_index in range(*prey_index_range):
      if not self.state.get_object_availability(prey_object_index):
        continue
      prey_pos = self.state.get_object_pos(prey_object_index)
      for predator_pos in predator_pos_list:
        if self._is_distance_in_po(prey_pos, predator_pos):
          distances = self._get_moved_away_distances(prey_pos, predator_pos)
          action_index = np.argmax(distances)
          distance = distances[action_index]
          weight = self.action_weight[action_index]
          weighted_actions[action_index] += weight / distance
      # Add noises to the weighted actions
      weighted_actions = self._get_noised_values(weighted_actions)
      # Update the cached action only if it's empty
      if not self.cached_action[prey_object_index]:
        action_index = np.argmax(weighted_actions)
        self.cached_action[prey_object_index] = self.actions[action_index]

  def _update_agent_pos(self):
    intended_pos = self._get_intended_pos()
    to_continue = True
    # Avoid overlapping positions
    while to_continue:
      to_continue = False
      overlapping_pos = self._get_overlapping_pos(intended_pos)
      for _, object_index_list in overlapping_pos.items():
        if not self._is_overlapping_allowed(object_index_list):
          # Restore the position
          for object_index in object_index_list:
            intended_pos[object_index] = self.state.get_object_pos(
                object_index)
            to_continue = True
    for object_index, pos in enumerate(intended_pos):
      self.state.set_object_pos(object_index, pos)

  def _update_prey_availabilities(self):
    # Get index ranges
    predator_index_range = self.get_group_index_range('PREDATOR')
    prey_index_range = self.get_group_index_range('PREY')
    # Get predator positions
    predator_pos_list = [self.state.get_object_pos(object_index)
                         for object_index in range(*predator_index_range)]
    # Reset cached reward
    self.cached_reward = 0.0
    # Check overlapping positions
    for prey_object_index in range(*prey_index_range):
      if not self.state.get_object_availability(prey_object_index):
        continue
      prey_pos = self.state.get_object_pos(prey_object_index)
      if prey_pos in predator_pos_list:
        self.state.set_object_availability(prey_object_index, False)
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

  def _is_overlapping_allowed(self, object_index_list):
    if len(object_index_list) == 1:
      return True
    if len(object_index_list) == 2:
      group_name_list = [self.get_group_name(object_index)
                         for object_index in object_index_list]
      sorted_group_name_list = sorted(group_name_list)
      if sorted_group_name_list == ['PREDATOR', 'PREY']:
        return True
    return False

  def _is_distance_in_po(self, pos1, pos2):
    distance = self._get_pos_distance(pos1, pos2)
    po_distance = self.options.po_radius
    return distance <= po_distance

  def _get_intended_pos(self):
    intended_pos = [None for _ in range(self.options.get_total_object_size())]
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
    moved_pos_list = [None for _ in self.actions]
    for action_index, action in enumerate(self.actions):
      moved_pos = self._get_moved_pos(pos_move, action)
      no_overlap = self.state.get_pos_status(moved_pos) is None
      in_field = moved_pos in self.map_data.field
      if no_overlap and in_field:
        moved_pos_list[action_index] = moved_pos
      else:
        moved_pos_list[action_index] = pos_move
    distances = [self._get_pos_distance(moved_pos, pos_ref)
                 for moved_pos in moved_pos_list]
    return distances

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

  def _get_pos_distance(self, pos1, pos2):
    vec = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
    return np.linalg.norm(vec)

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
  # * frame_skip_index: Current frame skipping index, starting from 0, resetting
  # after it reaches the frame skip
  object_list = None

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
    # Initialize the object list
    total_object_size = self.env_options.get_total_object_size()
    self.object_list = [{} for _ in range(total_object_size)]
    for group_name in self.env.group_names:
      index_range = self.env.get_group_index_range(group_name)
      for object_index in range(*index_range):
        self.set_object_group(object_index, group_name)
        self.set_object_pos(object_index, None)
        self.set_object_availability(object_index, True)
        self.set_object_action(object_index, 'STAND')
        self.set_object_frame_skip_index(object_index, 0)
    # Reset position map
    self._reset_pos_map()
    # Randomize the agent statuses
    self.randomize()
    # Initialize the time step
    self.time_step = 0

  def randomize(self):
    free_pos = copy.deepcopy(self.map_data.field)
    random.shuffle(free_pos)
    for group_name in self.env.group_names:
      index_range = self.env.get_group_index_range(group_name)
      for object_index in range(*index_range):
        pos = free_pos[object_index]
        self.set_object_pos(object_index, pos)

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
    # Remove old position from map
    old_pos = self.object_list[object_index].get('pos', None)
    if old_pos:
      old_pos_tuple = tuple(old_pos)
      self.pos_map.pop(old_pos_tuple, None)
    # Set position in map
    if pos:
      pos_tuple = tuple(pos)
      self.pos_map[pos_tuple] = object_index
    # Set object list
    self.object_list[object_index]['pos'] = pos

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
    old_frame_skip_index = self.object_list[object_index]['frame_skip_index']
    new_frame_skip_index = (old_frame_skip_index + 1) % frame_skip
    self.object_list[object_index]['frame_skip_index'] = new_frame_skip_index

  def increase_time_step(self):
    self.time_step += 1

  def get_pos_status(self, pos):
    pos_tuple = tuple(pos)
    return self.pos_map.get(pos_tuple, None)

  def get_po_symbolic_view(self, pos, radius):
    """Get partially observable (po) symbolic view.

    The returned view is always a square with the length of (2 * radius + 1).
    The position is always centered. The default background is black if the
    cropped image is near the boundaries.

    Args:
      pos (Array-like): The position of partially observable area.
      radius (int): The radius of partially observable area.

    Returns:
      numpy.ndarray: Partially observable symbolic view. Each value is the
      object index beginning from 0. If there is no object, the value will be
      -1.
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
          po_view[x_paste, y_paste] = self.env.group_names.index(group)
    return po_view

  def get_symbolic_positions(self):
    """Get symbolic positions.

    Returns:
      numpy.ndarray: Symbolic positions for each object in order: [x1, y1, x2,
      y2, ..., xn, yn] where n is the total object size.
    """
    total_object_size = self.env_options.get_total_object_size()
    positions = np.zeros(2 * total_object_size)
    for object_index in range(total_object_size):
      pos = self.get_object_pos(object_index)
      positions[2 * object_index + 0] = pos[0]
      positions[2 * object_index + 1] = pos[1]
    return positions

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
