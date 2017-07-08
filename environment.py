class EnvironmentState(object):
  """The internal state of the environment.
  """
  # Action
  actions = [
      'MOVE_RIGHT',
      'MOVE_UP',
      'MOVE_LEFT',
      'MOVE_DOWN',
      'IDLE'
  ]

  # Bounds (x, y, w, h)
  bounds = (1, 0, 7, 6)

  # Player
  player = [
      {
          'pos': (2, 2),
          'ball': True,
      },
      {
          'pos': (4, 2),
          'ball': False,
      },
  ]

  def take_action(self, index, action):
    pos = self.get_player_pos(index)
    if action == 'MOVE_RIGHT':
      pos[0] += 1
    elif action == 'MOVE_UP':
      pos[1] -= 1
    elif action == 'MOVE_LEFT':
      pos[0] -= 1
    elif action == 'MOVE_DOWN':
      pos[1] += 1
    elif action == 'IDLE':
      pass
    else:
      raise ValueError('Unknown action {}'.format(action))
    if self.is_pos_in_bounds(pos):
      self.set_player_pos(index, pos)

  def get_player_pos(self, index):
    return self.player[index]['pos']

  def set_player_pos(self, val):
    (index, pos) = val
    if self.is_pos_in_bounds(pos):
      self.player[index]['pos'] = pos

  def get_player_ball(self, index):
    return self.player[index]['ball']

  def set_player_ball(self, index, has_ball):
    self.player[index]['ball'] = has_ball

  def is_pos_in_bounds(self, pos):
    return (pos[0] >= self.bounds[0] and
            pos[1] >= self.bounds[1] and
            pos[0] < self.bounds[0] + self.bounds[2] and
            pos[1] < self.bounds[1] + self.bounds[3])
