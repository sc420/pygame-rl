#!/usr/bin/env python3
"""Sample: Interacting with the environment with minimal setup.
"""

# Native modules
import os
import random

# Third-party modules
import gym
import scipy.misc

# User-defined modules
import pygame_rl.scenario.gridworld as gridworld


def main():
    # Create an environment
    env = gym.make('gridworld-v0')

    # Run many episodes
    for episode_index in range(10):
        # Print the episode number
        print('')
        print('Episode {}:'.format(episode_index + 1))
        # Reset the environment
        state = env.reset()
        # Print the initial state
        print('Initial state:\n{}\n'.format(state))
        # Run the episode
        done = False
        timestep = 0
        while not done:
            # Render the environment
            env.render()
            # # Get the screenshot
            # screenshot = env.renderer.get_screenshot()
            # Take random action
            random_action = env.action_space.sample()
            # Update the environment
            next_state, reward, done, _ = env.step(random_action)
            # Print the status
            print('Timestep: {}'.format(timestep + 1))
            print('Reward: {}'.format(reward))
            # Transition to the next state
            state = next_state
            timestep += 1

    # # Save the last screenshot
    # env.render()
    # screenshot = env.renderer.get_screenshot()
    # screenshot_relative_path = 'screenshot.png'
    # screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    # scipy.misc.imsave(screenshot_abs_path, screenshot)
    # print('The last screenshot is saved to {}'.format(screenshot_abs_path))


if __name__ == '__main__':
    main()
