# Native modules
import random

# Third-party modules
import pytest

# Testing targets
import pygame_soccer.soccer.soccer_environment as soccer_environment


class SoccerEnvironmentTest(object):
  env = None
  state = None
  player_index = None
  computer_index = None

  @classmethod
  def setup_class(cls):
    # Initialize the environment
    env_options = soccer_environment.SoccerEnvironmentOptions(team_size=2)
    cls.env = soccer_environment.SoccerEnvironment(env_options=env_options)
    # Get the environment state
    cls.state = cls.env.state
    # Get the agent indexes
    cls.player_index = [cls.env.get_agent_index('PLAYER', team_index)
                        for team_index in range(2)]
    cls.computer_index = [cls.env.get_agent_index('COMPUTER', team_index)
                          for team_index in range(2)]

  @pytest.mark.parametrize('seed', range(100))
  def test_adjacent(self, seed):
    # Set the random seed
    random.seed(seed)
    # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [6, 0])
    self.state.set_agent_pos(self.player_index[1], [6, 1])
    self.state.set_agent_pos(self.computer_index[0], [7, 0])
    self.state.set_agent_pos(self.computer_index[1], [7, 1])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
    # Give the ball to player 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.player_index[0])
    # Take the action
    self.env.take_action(['STAND', 'STAND'])
    # The player positions should have not changed
    assert self.state.get_agent_pos(self.player_index[0]) == [6, 0]
    assert self.state.get_agent_pos(self.player_index[1]) == [6, 1]
    # The computer positions should have either not changed or swapped
    possible_pos = [[7, 0], [7, 1]]
    assert self.state.get_agent_pos(self.computer_index[0]) in possible_pos
    assert self.state.get_agent_pos(self.computer_index[1]) in possible_pos
    # Either the player 1 still have the ball, or the computer 1 got the ball
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    assert (ball_agent_index == self.player_index[0]
            or ball_agent_index == self.computer_index[0])

  @pytest.mark.parametrize('seed', range(100))
  def test_avoid_opponent(self, seed):
    # Set the random seed
    random.seed(seed)
    # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [1, 2])
    self.state.set_agent_pos(self.player_index[1], [1, 3])
    self.state.set_agent_pos(self.computer_index[0], [7, 2])
    self.state.set_agent_pos(self.computer_index[1], [7, 3])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'DEFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'DEFENSIVE')
    # Give the ball to computer 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.computer_index[0])
    # Take the action
    self.env.take_action(['MOVE_RIGHT', 'MOVE_RIGHT'])
    # The computer 1 should avoid player 1
    assert self.state.get_agent_pos(self.computer_index[0]) == [8, 2]
    # The computer 2 should approach the nearest goal position against player 2
    assert self.state.get_agent_pos(self.computer_index[1]) == [8, 3]

  @pytest.mark.parametrize('seed', range(100))
  def test_advance_to_goal(self, seed):
    # Set the random seed
    random.seed(seed)
   # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [1, 2])
    self.state.set_agent_pos(self.player_index[1], [1, 3])
    self.state.set_agent_pos(self.computer_index[0], [7, 2])
    self.state.set_agent_pos(self.computer_index[1], [7, 3])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
    # Give the ball to computer 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.computer_index[0])
    # Take the action
    self.env.take_action(['MOVE_RIGHT', 'MOVE_RIGHT'])
    # The computer 1 should approach the furthest goal position against player 1
    assert self.state.get_agent_pos(self.computer_index[0]) == [6, 2]
    # The computer 2 should intercept against player 2
    assert self.state.get_agent_pos(self.computer_index[1]) == [6, 3]

  @pytest.mark.parametrize('seed', range(100))
  def test_defend_goal(self, seed):
    # Set the random seed
    random.seed(seed)
    # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [1, 2])
    self.state.set_agent_pos(self.player_index[1], [1, 3])
    self.state.set_agent_pos(self.computer_index[0], [7, 2])
    self.state.set_agent_pos(self.computer_index[1], [7, 3])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'DEFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'DEFENSIVE')
    # Give the ball to player 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.player_index[0])
    # Take the action
    self.env.take_action(['MOVE_RIGHT', 'MOVE_RIGHT'])
    # The computer 1 should approach the nearest goal position against player 1
    assert self.state.get_agent_pos(self.computer_index[0]) == [8, 2]
    # The computer 2 should approach the nearest goal position against player 1
    possible_pos = [[7, 2], [8, 3]]
    assert self.state.get_agent_pos(self.computer_index[1]) in possible_pos

  @pytest.mark.parametrize('seed', range(100))
  def test_intercept_goal(self, seed):
    # Set the random seed
    random.seed(seed)
    # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [1, 2])
    self.state.set_agent_pos(self.player_index[1], [1, 3])
    self.state.set_agent_pos(self.computer_index[0], [7, 2])
    self.state.set_agent_pos(self.computer_index[1], [7, 3])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
    # Give the ball to player 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.player_index[0])
    # Take the action
    self.env.take_action(['MOVE_RIGHT', 'MOVE_RIGHT'])
    # The computer 1 should intercept against player 1
    assert self.state.get_agent_pos(self.computer_index[0]) == [6, 2]
    # The computer 2 should intercept against player 1
    assert self.state.get_agent_pos(self.computer_index[1]) == [6, 3]

  @pytest.mark.parametrize('seed', range(100))
  def test_negative_reward(self, seed):
    # Set the random seed
    random.seed(seed)
    # Set the initial positions
    self.state.set_agent_pos(self.player_index[0], [1, 2])
    self.state.set_agent_pos(self.player_index[1], [1, 3])
    self.state.set_agent_pos(self.computer_index[0], [7, 2])
    self.state.set_agent_pos(self.computer_index[1], [7, 3])
    # Set the computer agent modes
    self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
    self.state.set_agent_mode(self.computer_index[1], 'DEFENSIVE')
    # Give the ball to player 1
    ball_possession = self.state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    self.state.switch_ball(ball_agent_index, self.player_index[0])
    # The computer agent should score in 50 steps
    for _ in range(50):
      observation = self.env.take_action(['MOVE_UP', 'STAND'])
      if observation.next_state.is_team_win('COMPUTER'):
        break
    assert observation.reward == pytest.approx(-1.0)
