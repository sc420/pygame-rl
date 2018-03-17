#!/usr/bin/env python3
# pylint: disable=W0611
"""Sample: Interacting with the environment with minimal setup.
"""

# Native modules
import os

# Third-party modules
import gym
import scipy.misc

# User-defined modules
import pygame_rl.scenario.gridworld


def main():
    # Create an environment
    env = gym.make('gridworld-v0')

    # Load the enviornment
    env.load()

    # Run many episodes
    for episode_ind in range(10):
        # Print the episode number
        print('')
        print('Episode {}:'.format(episode_ind + 1))
        # Reset the environment
        state = env.reset()
        # Print the shape of initial state
        print('Shape of initial state:{}'.format(state.shape))
        # Run the episode
        done = False
        timestep = 0
        while not done:
            # Render the environment
            screenshot = env.render()
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

    # Save the last screenshot
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, screenshot)
    print('The last screenshot is saved to {}'.format(screenshot_abs_path))


if __name__ == '__main__':
    main()
