#!/usr/bin/env python3
"""Sample: Interacting with the environment with advanced usage.
"""

# Native modules
import os
import random

# Third-party modules
import numpy as np
import scipy.misc

# User-defined modules
import pygame_rl.scenario.predator_prey_environment as predator_prey_environment
import pygame_rl.util.file_util as file_util


def main():
  # Initialize the random number generator to have consistent results
  random.seed(0)

  # Resolve the map path relative to this file
  map_path = file_util.resolve_path(
      __file__, '../data/map/predator_prey/predator_prey_15x15.tmx')

  # Create an environment options
  object_size = {
      'PREDATOR': 3,
      'PREY': 3,
      'OBSTACLE': 8,
  }
  env_options = predator_prey_environment.PredatorPreyEnvironmentOptions(
      map_path=map_path, object_size=object_size, ai_frame_skip=2)

  # Create an environment
  env = predator_prey_environment.PredatorPreyEnvironment(
      env_options=env_options)

  # Get index range of preys
  prey_index_range = env.get_group_index_range('PREY')
  first_predator_index = range(*prey_index_range)[0]

  # Run many episodes
  for episode_index in range(10):
    # Print the episode number
    print('')
    print('Episode {}:'.format(episode_index + 1))
    # Reset the environment and get the initial observation
    observation = env.reset()
    state = observation.state
    action = observation.action
    reward = observation.reward
    next_state = observation.next_state
    # Print the state
    print('Initial state:\n({}, {}, {}, {})\n'.format(
        state, action, reward, next_state))
    # Run the episode
    is_running = True
    while is_running:
      # Render the environment
      env.render()
      # Get the partially observable screenshot of the first agent with a radius
      # of 1
      pos = np.array(env.state.get_object_pos(first_predator_index))
      po_screenshot = env.renderer.get_po_screenshot(pos, 2)
      # Take cached actions
      for object_index in range(*prey_index_range):
        # Get a random action from the action list
        action = random.choice(env.actions)
        # Take the cached action
        env.take_cached_action(object_index, action)
      # Update the environment and get observation
      observation = env.update_state()
      # Check the terminal state
      if env.state.is_terminal():
        print('Terminal state:\n{}'.format(observation))
        print('Episode {} ends at time step {}'.format(
            episode_index + 1, env.state.time_step + 1))
        is_running = False

  # Save the last partially observable screenshot
  env.render()
  pos = np.array(env.state.get_object_pos(first_predator_index))
  po_screenshot = env.renderer.get_po_screenshot(pos, 2)
  screenshot_relative_path = 'screenshot.png'
  screenshot_abs_path = os.path.abspath(screenshot_relative_path)
  scipy.misc.imsave(screenshot_abs_path, po_screenshot)
  print('The last partially observable screenshot is saved to {}'.format(
      screenshot_abs_path))


if __name__ == '__main__':
  main()
