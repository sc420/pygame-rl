"""Sample: Interacting with the environment with minimal setup.
"""

# Native modules
import os

# Third-party modules
import gym
import scipy.misc

# User-defined modules
from pygame_rl.scenario.soccer.actions import Actions
import pygame_rl.scenario.soccer


def main():
    # Create a soccer environment
    env = gym.make('soccer-v0')

    # Load the environment
    env.load()

    # Run many episodes
    for ep_idx in range(20):
        # Print the episode number
        print('')
        print('Episode {}:'.format(ep_idx + 1))
        # Reset the environment
        state = env.reset()
        # Print the initial state
        print('Initial state:\n{}\n'.format(state))
        # Run the episode
        while True:
            # Render the environment
            screenshot = env.render()
            # Get random actions
            actions = env.action_space.sample()
            # Reset the computer action because we don't want to control it
            actions[1] = Actions.NOOP
            # Interact with the environment
            new_state, reward, done, _ = env.step(actions)
            # Check the terminal state
            if done:
                print('Terminal state:\n{}\nReward: {}'.format(new_state, reward))
                break
            # Transition the state
            state = new_state

    # Save the last screenshot
    screenshot = env.render()
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, screenshot)
    print('The last screenshot is saved to {}'.format(screenshot_abs_path))


if __name__ == '__main__':
    main()
