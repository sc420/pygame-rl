# Native modules
import random

# User-defined modules
from soccer.environment import Environment
from soccer.soccer_renderer import SoccerRenderer


class SoccerEnvironment(Environment):
  """The soccer environment.
  """
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

  # Bounds list (x, y, w, h)
  bounds_list = [
      # Field
      [1, 0, 7, 6],
      # Left goal
      [0, 2, 1, 2],
      # Right goal
      [8, 2, 1, 2],
  ]

  # Renderer
  renderer = None
  renderer_loaded = False

  def __init__(self):
    self.state = SoccerState()
    self.renderer = SoccerRenderer(self)

  def reset(self):
    self.state.randomize()
    return SoccerObservation(self.state, None, 0.0, None)

  def take_action(self, action):
    # The player index is always 0
    player_ind = 0
    # Do the action
    pos = list(self.state.get_player_pos(player_ind))
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
      raise ValueError('Unknown action {}'.format(action))
    if is_pos_in_bounds(self.bounds_list, pos):
      self.state.set_player_pos(player_ind, pos)
    # Return the observation, the original state is not returned to increase
    # the speed, otherwise deep copying must be used before changing the
    # position.
    return SoccerObservation(None, action, 0.0, self.state)

  def render(self):
    # Lazy load the renderer
    if not self.renderer_loaded:
      self.renderer.load()
      self.renderer_loaded = True
    # Render
    self.renderer.render()


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
  # Spawn bounds list for randomization (x, y, w, h)
  spawn_bounds_list = [
      # Left half
      [1, 0, 3, 6],
      # Right half
      [5, 0, 3, 6],
  ]

  # Goal bounds list (x, y, w, h)
  goal_bounds_list = [
      # Left goal
      [0, 2, 1, 2],
      # Right goal
      [8, 2, 1, 2],
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

  def __init__(self):
    self.randomize()

  def is_terminal(self):
    for player in self.player_list:
      return is_pos_in_bounds(self.goal_bounds_list, player['pos'])

  def randomize(self):
    # Randomize the player position
    for player_ind in range(len(self.spawn_bounds_list)):
      spawn_bounds = self.spawn_bounds_list[player_ind]
      player = self.player_list[player_ind]
      x_range = [spawn_bounds[0], spawn_bounds[0] + spawn_bounds[2]]
      y_range = [spawn_bounds[1], spawn_bounds[1] + spawn_bounds[3]]
      player['pos'] = [
          random.randrange(*x_range),
          random.randrange(*y_range),
      ]
    # Randomize the possession of the ball
    has_ball = random.choice([True, False])
    self.player_list[0]['ball'] = has_ball
    self.player_list[1]['ball'] = not has_ball

  def get_player_pos(self, index):
    return self.player_list[index]['pos']

  def set_player_pos(self, index, pos):
    self.player_list[index]['pos'] = pos

  def get_player_ball(self, index):
    return self.player_list[index]['ball']

  def set_player_ball(self, index, has_ball):
    self.player_list[index]['ball'] = has_ball

  def __repr__(self):
    return 'Player 1: {}, Player 2: {}, Ball possession: {}'.format(
        self.player_list[0]['pos'],
        self.player_list[1]['pos'],
        1 if self.player_list[0]['ball'] else 2)

  def __eq__(self, other):
    if not isinstance(other, SoccerState):
      return False
    return self.player_list == other.player_list

  def __hash__(self):
    hash_list = []
    for player in self.player_list:
      hash_list.extend(player['pos'])
      hash_list.append(player['ball'])
    return hash(tuple(hash_list))


def is_pos_in_bounds(bounds_list, pos):
  for bounds in bounds_list:
    in_bounds = (pos[0] >= bounds[0]
                 and pos[1] >= bounds[1]
                 and pos[0] < bounds[0] + bounds[2]
                 and pos[1] < bounds[1] + bounds[3])
    if in_bounds:
      return True
  return False
