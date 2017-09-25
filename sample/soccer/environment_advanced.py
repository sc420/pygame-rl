#!/usr/bin/env python3
"""Sample: Interacting with the environment with advanced usage.
"""

# Native modules
import os
import random

# Third-party modules
import scipy.misc

# User-defined modules
import pygame_rl.soccer.soccer_environment as soccer_environment
import pygame_rl.util.file_util as file_util


def main():
  # Initialize the random number generator to have consistent results
  random.seed(0)

  # Resolve the map path relative to this file
  map_path = file_util.resolve_path(__file__, 'data/map/soccer_large.tmx')

  # Create a soccer environment options
  # "map_data" is specified to use the custom map.
  # "team_size" is given to specify the agents in one team.
  # "ai_frame_skip" is to control the frame skip for AI only
  env_options = soccer_environment.SoccerEnvironmentOptions(
      map_path=map_path, team_size=2, ai_frame_skip=2)

  # Create a soccer environment
  # If you want to render the environment, an optional argument
  # "renderer_options" can be used. For the sample usage, see
  # "sample/renderer.py".
  soccer_env = soccer_environment.SoccerEnvironment(env_options=env_options)

  # Run many episodes
  for episode_index in range(20):
    # Print the episode number
    print('')
    print('Episode {}:'.format(episode_index + 1))
    # Reset the environment and get the initial observation. The observation is
    # a class defined as "soccer_environment.SoccerObservation".
    observation = soccer_env.reset()
    state = observation.state
    action = observation.action
    reward = observation.reward
    next_state = observation.next_state
    # Print the state, action, reward, and next state pair
    print('Initial state:\n({}, {}, {}, {})\n'.format(
        state, action, reward, next_state))
    # Run the episode
    is_running = True
    while is_running:
      # Render the environment. The renderer will lazy load on the first call.
      # Skip the call if you don't need the rendering.
      soccer_env.render()
      # Get the partially observable screenshot of the first agent with a radius
      # of 1. The returned `screenshot` is a `numpy.ndarray`, the format is the
      # same as the returned value of `scipy.misc.imread`. The previous call is
      # required for this call to work.
      po_screenshot = soccer_env.renderer.get_po_screenshot(0, 1)
      # Build a list of randomly chosen actions
      actions = {}
      for team_name in soccer_env.team_names:
        for team_agent_index in range(soccer_env.options.team_size):
          agent_index = soccer_env.get_agent_index(team_name, team_agent_index)
          actions[agent_index] = random.choice(soccer_env.actions)
      # Take the actions and get the observation
      observation = soccer_env.take_all_actions(actions)
      # Check the terminal state
      if soccer_env.state.is_terminal():
        print('Terminal state:\n{}'.format(observation))
        print('Episode {} ends at time step {}'.format(
            episode_index + 1, soccer_env.state.time_step + 1))
        is_running = False

  # Save the last partially observable screenshot
  soccer_env.render()
  po_screenshot = soccer_env.renderer.get_po_screenshot(0, 1)
  screenshot_relative_path = 'screenshot.png'
  screenshot_abs_path = os.path.abspath(screenshot_relative_path)
  scipy.misc.imsave(screenshot_abs_path, po_screenshot)
  print('The last partially observable screenshot is saved to {}'.format(
      screenshot_abs_path))


if __name__ == '__main__':
  main()
