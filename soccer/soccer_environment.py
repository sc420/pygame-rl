# Native modules
import random

# Third-party modules
import numpy as np

# User-defined modules
from renderer.file_util import resolve_path
from renderer.pygame_util import TiledData
from soccer.environment import Environment
from soccer.soccer_renderer import SoccerRenderer


class SoccerEnvironment(Environment):
  """The soccer environment.
  """
  # Map path relative to this file
  map_relative_path = '../data/map/soccer.tmx'

  # State
  state = None

  # Action
  actions = [
      'MOVE_RIGHT',
      'MOVE_UP',
      'MOVE_LEFT',
      'MOVE_DOWN',
      'STAND',
  ]

  # Positions
  soccer_pos = None

  # Renderer
  renderer = None
  renderer_loaded = False

  def __init__(self, renderer_options=None):
    # Resolve the map absolute path
    map_path = resolve_path(__file__, self.map_relative_path)
    # Load the tile positions
    self.soccer_pos = SoccerPosition(map_path)
    # Initialize the state
    self.state = SoccerState(self.soccer_pos)
    # Initialize the renderer
    self.renderer = SoccerRenderer(map_path, self, renderer_options)

  def reset(self):
    self.state.reset()
    return SoccerObservation(self.state, None, 0.0, None)

  def take_action(self, action):
    # Select the agent indexes
    player_ind = 0
    computer_ind = 1
    # Calculate the positions of the two agents
    player_pos = self.state.get_player_pos(player_ind)
    player_moved_pos = self.get_moved_pos(player_pos, action)
    computer_moved_pos = self.get_computer_moved_pos()
    # Randomly let one of the agent take the action first
    if random.choice([player_ind, computer_ind]) == player_ind:
      self.update_agent_pos(player_ind, player_moved_pos)
      self.update_agent_pos(computer_ind, computer_moved_pos)
    else:
      self.update_agent_pos(computer_ind, computer_moved_pos)
      self.update_agent_pos(player_ind, player_moved_pos)
    # Increase the time step
    self.state.increase_time_step()
    # Determine the reward
    if self.state.is_player_win(player_ind):
      reward = 1.0
    else:
      reward = 0.0
    # Return the observation, the original state is not returned to increase
    # the speed, otherwise deep copying must be used before changing the
    # position.
    return SoccerObservation(None, action, reward, self.state)

  def render(self):
    # Lazy load the renderer
    if not self.renderer_loaded:
      self.renderer.load()
      self.renderer_loaded = True
    # Render
    self.renderer.render()

  def update_agent_pos(self, agent_ind, pos):
    if pos in self.soccer_pos.walkable:
      update = True
      # Check whether one agent loses his ball
      other_agent_index = self.state.get_other_agent_index(agent_ind)
      if pos == self.state.get_player_pos(other_agent_index):
        self.state.switch_ball()
        update = False
      # Update the position if the agent hasn't lost the ball
      if update:
        self.state.set_player_pos(agent_ind, pos)

  def get_computer_moved_pos(self):
    # Select the agent indexes
    player_ind = 0
    computer_ind = 1
    # Get the state info
    has_ball = self.state.get_player_ball(computer_ind)
    agent_mode = self.state.computer_agent_mode
    # Choose the target position
    player_pos = self.state.get_player_pos(player_ind)
    computer_pos = self.state.get_player_pos(computer_ind)
    if agent_mode == 'DEFENSIVE':
      if has_ball:
        target_pos = player_pos
        strategic_mode = 'AVOID'
      else:
        # Calculate the distance from the player
        goals = self.soccer_pos.goals['player']
        distances = [self.get_pos_distance(goal_pos, player_pos)
                     for goal_pos in goals]
        # Select the minimum distance
        min_distance_ind = np.argmin(distances)
        target_pos = goals[min_distance_ind]
        strategic_mode = 'APPROACH'
    elif agent_mode == 'OFFENSIVE':
      if has_ball:
        # Calculate the distance from the player
        goals = self.soccer_pos.goals['computer']
        distances = [self.get_pos_distance(goal_pos, player_pos)
                     for goal_pos in goals]
        # Select the minimum distance
        min_distance_ind = np.argmax(distances)
        target_pos = goals[min_distance_ind]
        strategic_mode = 'APPROACH'
      else:
        target_pos = player_pos
        strategic_mode = 'APPROACH'
    else:
      raise KeyError('Unknown computer agent mode {}'.format(agent_mode))
    # Get the strategic action
    action = self.get_strategic_action(
        computer_pos, target_pos, strategic_mode)
    # Calculate the moved position
    moved_pos = self.get_moved_pos(computer_pos, action)
    return moved_pos

  def get_strategic_action(self, source_pos, target_pos, mode):
    # Calculate the original Euclidean distance
    orig_dist = self.get_pos_distance(source_pos, target_pos)
    # Find the best action
    best_action = random.choice(self.actions)
    best_dist = orig_dist
    # Shuffle the actions
    shuffled_actions = random.sample(self.actions, len(self.actions))
    # Find the best action
    for action in shuffled_actions:
      # Get the moved position after doing the action
      moved_pos = self.get_moved_pos(source_pos, action)
      # Check whether the moved position is valid
      if not moved_pos in self.soccer_pos.walkable:
        continue
      # Calculate the new Euclidean distance
      moved_dist = self.get_pos_distance(moved_pos, target_pos)
      if mode == 'APPROACH':
        if (best_dist is None) or (moved_dist < best_dist):
          best_action = action
          best_dist = moved_dist
      elif mode == 'AVOID':
        if (best_dist is None) or (moved_dist > best_dist):
          best_action = action
          best_dist = moved_dist
      else:
        raise KeyError('Unknown mode {}'.format(mode))
    return best_action

  def get_moved_pos(self, pos, action):
    # Copy the position
    pos = list(pos)
    # Move to the 4-direction grid
    if action == 'MOVE_RIGHT':
      pos[0] += 1
    elif action == 'MOVE_UP':
      pos[1] -= 1
    elif action == 'MOVE_LEFT':
      pos[0] -= 1
    elif action == 'MOVE_DOWN':
      pos[1] += 1
    elif action == 'STAND':
      pass
    else:
      raise KeyError('Unknown action {}'.format(action))
    return pos

  def get_pos_distance(self, pos1, pos2):
    vec = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
    return np.linalg.norm(vec)


class SoccerPosition(object):
  """The soccer position as the geographical info.
  """
  # Tile positions
  walkable = []
  goals = []

  def __init__(self, map_path):
    # Create a tile data and load
    tiled_data = TiledData(map_path)
    tiled_data.load()
    # Get the background tile positions
    tile_pos = tiled_data.get_background_tile_positions()
    # Build the tile positions
    self.walkable = tile_pos['ground']['walkable']
    self.goals = tile_pos['goal']


class SoccerObservation(object):
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
    return 'State: {}\nAction: {}\nReward: {}\nNext state: {}'.format(
        self.state, self.action, self.reward, self.next_state)


class SoccerState(object):
  """The internal soccer state.
  """
  # Computer agent mode list
  computer_agent_mode_list = [
      'DEFENSIVE',
      'OFFENSIVE',
  ]

  # Player list as the state, the initial position and ball possession should
  # not be used.
  player_list = [{
      'pos': [3, 2],
      'ball': True,
  }, {
      'pos': [5, 2],
      'ball': False,
  }]

  # Computer agent mode, the initial mode should not be used.
  computer_agent_mode = 'DEFENSIVE'

  # Time step
  time_step = 0

  # Soccer position
  soccer_pos = None

  # Spawn bounds list for randomization (x, y, w, h)
  spawn_bounds_list = [
      # Left half
      [1, 0, 3, 6],
      # Right half
      [5, 0, 3, 6],
  ]

  def __init__(self, soccer_pos):
    self.soccer_pos = soccer_pos
    self.randomize()

  def reset(self):
    self.randomize()
    self.time_step = 0

  def is_terminal(self):
    # When the time step exceeds 100
    if self.time_step >= 100:
      return True
    # When one of the agent reaches the goal
    for player_ind in range(len(self.player_list)):
      if self.is_player_win(player_ind):
        return True
    # Otherwise, the state isn't terminal
    return False

  def randomize(self):
    # Randomize the player positions
    for player_ind in range(len(self.spawn_bounds_list)):
      spawn_bounds = self.spawn_bounds_list[player_ind]
      x_range = [spawn_bounds[0], spawn_bounds[0] + spawn_bounds[2]]
      y_range = [spawn_bounds[1], spawn_bounds[1] + spawn_bounds[3]]
      player_pos = [
          random.randrange(*x_range),
          random.randrange(*y_range),
      ]
      self.set_player_pos(player_ind, player_pos)
    # Randomize the possession of the ball
    has_ball = random.choice([True, False])
    self.set_player_ball(0, has_ball)
    self.set_player_ball(1, not has_ball)
    # Randomize the computer agent mode
    self.computer_agent_mode = random.choice(self.computer_agent_mode_list)

  def is_player_win(self, index):
    player_pos = self.get_player_pos(index)
    has_ball = self.get_player_ball(index)
    if not has_ball:
      return False
    index_to_goal_name = {
        0: 'player',
        1: 'computer',
    }
    goal_name = index_to_goal_name[index]
    return player_pos in self.soccer_pos.goals[goal_name]

  def get_player_pos(self, index):
    return self.player_list[index]['pos']

  def set_player_pos(self, index, pos):
    self.player_list[index]['pos'] = pos

  def get_player_ball(self, index):
    return self.player_list[index]['ball']

  def set_player_ball(self, index, has_ball):
    self.player_list[index]['ball'] = has_ball

  def set_computer_agent_mode(self, mode):
    self.computer_agent_mode = mode

  def increase_time_step(self):
    self.time_step += 1

  def switch_ball(self):
    if self.get_player_ball(0):
      self.set_player_ball(0, False)
      self.set_player_ball(1, True)
    else:
      self.set_player_ball(0, True)
      self.set_player_ball(1, False)

  def get_other_agent_index(self, index):
    if index == 0:
      return 1
    elif index == 1:
      return 0
    else:
      raise IndexError('The agent index should be either 0 or 1')

  def __repr__(self):
    format_str = ('Player 1: {}, Player 2: {}, Ball possession: {},'
                  ' Computer agent mode: {}, Time step: {}')
    return format_str.format(
        self.get_player_pos(0),
        self.get_player_pos(1),
        1 if self.get_player_ball(0) else 2,
        self.computer_agent_mode,
        self.time_step)

  def __eq__(self, other):
    if not isinstance(other, SoccerState):
      return False
    return self.player_list == other.player_list

  def __hash__(self):
    hash_list = []
    for player_ind in range(len(self.player_list)):
      hash_list.extend(self.get_player_pos(player_ind))
      hash_list.append(self.get_player_ball(player_ind))
    return hash(tuple(hash_list))
