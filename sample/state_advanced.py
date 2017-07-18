#!/usr/bin/env python3
"""Sample: Interacting with the environment state with advanced usage.
"""

# Native modules
import random

# User-defined modules
import pygame_soccer.soccer.soccer_environment as soccer_environment


def main():
  # Initialize the random number generator to have consistent results
  random.seed(0)

  # Create a soccer environment
  soccer_env = soccer_environment.SoccerEnvironment()

  # Reset the environment.
  soccer_env.reset()

  # Get the current state. The state is a class defined as
  # "soccer_environment.SoccerState".
  state = soccer_env.state

  # Get the team names
  player_team_name = soccer_env.team_names[0]
  computer_team_name = soccer_env.team_names[1]

  # Get the modes
  offensive_mode = soccer_env.modes[1]

  # Get the actions
  move_right_action = soccer_env.actions[0]

  # Get the agent indexes of the first player in player and computer teams
  player_agent_index = soccer_env.get_agent_index(player_team_name, 0)
  computer_agent_index = soccer_env.get_agent_index(computer_team_name, 0)

  # Move the player agent position to be one step from the rightmost goal field
  player_pos = [7, 2]
  state.set_agent_pos(player_agent_index, player_pos)

  # Get the player agent position
  player_pos = state.get_agent_pos(player_agent_index)

  # Move the computer agent position to be two steps left to the player
  computer_pos = list(player_pos)
  computer_pos[0] -= 2
  state.set_agent_pos(computer_agent_index, computer_pos)

  # Make the player possess the ball
  state.set_agent_ball(player_agent_index, True)
  state.set_agent_ball(computer_agent_index, False)

  # Set the computer agent mode to be offensive
  state.set_agent_mode(computer_agent_index, offensive_mode)

  # Take the moving right action
  soccer_env.take_action(move_right_action)

  # Get the last taken action of the computer agent
  computer_last_action = state.get_agent_action(computer_agent_index)
  print('The computer agent took the action {}'.format(computer_last_action))
  print('The computer should move right to approach the player')

  # Check if the player team has won
  player_team_is_win = state.is_team_win(player_team_name)
  print('Whether the player team has won: {}'.format(player_team_is_win))
  print('The player team should have won')

  # Check if the state is terminal
  is_terminal = state.is_terminal()
  print('Whether the state is terminal: {}'.format(is_terminal))
  print('The state should be terminal when one team won')


if __name__ == '__main__':
  main()
