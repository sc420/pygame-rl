#!/usr/bin/env python3
"""Sample: Interacting with the environment with minimal setup.
"""

# Native modules
import os
import random

# Third-party modules
import scipy.misc

# User-defined modules
import pygame_rl.scenario.predator_prey_environment as predator_prey_environment


def main():
    # Initialize the random number generator to have consistent results
    random.seed(0)

    # Create an environment
    env = predator_prey_environment.PredatorPreyEnvironment()

    # Get index range of predators
    predator_index_range = env.get_group_index_range('PREDATOR')

    # Run many episodes
    for episode_index in range(10):
        # Print the episode number
        print('')
        print('Episode {}:'.format(episode_index + 1))
        # Reset the environment
        observation = env.reset()
        # Print the initial state
        print('Initial observation:\n{}\n'.format(observation))
        # Run the episode
        is_running = True
        while is_running:
            # Render the environment
            env.render()
            # Get the screenshot
            screenshot = env.renderer.get_screenshot()
            # Take cached actions
            for predator_index in range(*predator_index_range):
                # Get a random action from the action list
                action = random.choice(env.actions)
                # Take the cached action
                env.take_cached_action(predator_index, action)
            # Update the environment and get observation
            observation = env.update_state()
            # Check the terminal state
            if env.state.is_terminal():
                print('Terminal observation:\n{}'.format(observation))
                print('Episode {} ends at time step {}'.format(
                    episode_index + 1, env.state.time_step + 1))
                is_running = False

    # Save the last screenshot
    env.render()
    screenshot = env.renderer.get_screenshot()
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, screenshot)
    print('The last screenshot is saved to {}'.format(screenshot_abs_path))


if __name__ == '__main__':
    main()
