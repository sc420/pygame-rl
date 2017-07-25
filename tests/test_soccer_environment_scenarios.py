# Native modules
import random

# Third-party modules
import pytest

# Testing targets
import pygame_soccer.soccer.soccer_environment as soccer_environment


class SoccerEnvironmentTest:
  env = None

  @classmethod
  def setup_class(cls):
    random.seed(4)

    env_options = soccer_environment.SoccerEnvironmentOptions(team_size=2)
    cls.env = soccer_environment.SoccerEnvironment(env_options=env_options)

  @pytest.mark.parametrize('seed', range(100))
  def test_adjacent(self, seed):
    # Set the random seed
    random.seed(seed)
    # Get the environment state
    state = self.env.state
    # Get the agent indexes
    player_index = [self.env.get_agent_index('PLAYER', team_index)
                    for team_index in range(2)]
    computer_index = [self.env.get_agent_index('COMPUTER', team_index)
                      for team_index in range(2)]
    # Set the initial positions
    state.set_agent_pos(player_index[0], [6, 0])
    state.set_agent_pos(player_index[1], [6, 1])
    state.set_agent_pos(computer_index[0], [7, 0])
    state.set_agent_pos(computer_index[1], [7, 1])
    # Set the computer agent modes
    state.set_agent_mode(computer_index[0], 'OFFENSIVE')
    state.set_agent_mode(computer_index[1], 'OFFENSIVE')
    # Give the ball to the player 1
    ball_possession = state.get_ball_possession()
    state.switch_ball(ball_possession['agent_index'], player_index[0])
    # Take the action
    self.env.take_action(['STAND', 'STAND'])
    # The player positions should have not changed
    assert state.get_agent_pos(player_index[0]) == [6, 0]
    assert state.get_agent_pos(player_index[1]) == [6, 1]
    # The computer positions should have either not changed or swapped
    possible_computer_pos = [[7, 0], [7, 1]]
    assert state.get_agent_pos(computer_index[0]) in possible_computer_pos
    assert state.get_agent_pos(computer_index[1]) in possible_computer_pos
    # Either the player 1 still have the ball, or the computer 1 got the ball
    ball_possession = state.get_ball_possession()
    ball_agent_index = ball_possession['agent_index']
    assert (ball_agent_index == player_index[0]
            or ball_agent_index == computer_index[0])
