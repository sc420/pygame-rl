#!/usr/bin/env python3
"""Sample: Interacting with the legacy environment.
"""

# Native modules
import os
import random

# Third-party modules
import scipy.misc

# User-defined modules
import pygame_rl.scenario.soccer_environment as soccer_environment


def main():
    # Initialize the random number generator to have consistent results
    random.seed(0)

    # Create a soccer environment
    soccer_env = soccer_environment.SoccerLegacyEnvironment()

    # Run many episodes
    for episode_index in range(20):
        # Print the episode number
        print('')
        print('Episode {}:'.format(episode_index + 1))
        # Reset the environment
        observation = soccer_env.reset()
        # Print the initial state
        print('Initial state:\n{}\n'.format(observation))
        # Run the episode
        is_running = True
        while is_running:
            # Render the environment
            soccer_env.render()
            # Get the screenshot
            screenshot = soccer_env.renderer.get_screenshot()
            # Get a random action from the action list
            action = random.choice(soccer_env.actions)
            # Take the action and get the observation
            observation = soccer_env.take_action(action)
            # Check the terminal state
            if soccer_env.state.is_terminal():
                print('Terminal state:\n{}'.format(observation))
                print('Episode {} ends at time step {}'.format(
                    episode_index + 1, soccer_env.state.time_step + 1))
                is_running = False

    # Save the last screenshot
    soccer_env.render()
    screenshot = soccer_env.renderer.get_screenshot()
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, screenshot)
    print('The last screenshot is saved to {}'.format(screenshot_abs_path))


if __name__ == '__main__':
    main()
