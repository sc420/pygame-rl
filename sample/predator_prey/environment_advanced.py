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
        map_path=map_path, object_size=object_size, po_radius=3,
        ai_frame_skip=2)

    # Create an environment
    env = predator_prey_environment.PredatorPreyEnvironment(
        env_options=env_options)

    # Get index range of preys
    predator_index_range = env.get_group_index_range('PREDATOR')
    first_predator_index = range(*predator_index_range)[0]

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
            # Get position of the first predator
            pos = np.array(env.state.get_object_pos(first_predator_index))
            # Get partially observable symbolic view of the first agent with a
            # radius of 2
            po_view = env.state.get_po_symbolic_view(pos, 2)
            # Get partially observable screenshot of the first agent with a
            # radius of 2
            po_screenshot = env.renderer.get_po_screenshot(pos, 2)
            # Build actions without obstacles
            actions_wo = [None] * (env.options.object_size['PREDATOR'] +
                                   env.options.object_size['PREY'])
            # Get a random action from the action list
            action = random.choice(env.actions)
            # Set the action of the first predator
            actions_wo[0] = action
            # Update the environment and get observation
            observation = env.step_without_obstacles(actions_wo)
            # Check the terminal state
            if env.state.is_terminal():
                print('Terminal state:\n{}'.format(observation))
                print('Episode {} ends at time step {}'.format(
                    episode_index + 1, env.state.time_step + 1))
                is_running = False

    # Get position of the first predator
    pos = np.array(env.state.get_object_pos(first_predator_index))

    # Print the last partially observable symbolic view
    po_view = env.state.get_po_symbolic_view(pos, 2)
    print(po_view)

    # Save the last partially observable screenshot
    env.render()
    po_screenshot = env.renderer.get_po_screenshot(pos, 2)
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, po_screenshot)
    print('The last partially observable screenshot is saved to {}'.format(
        screenshot_abs_path))


if __name__ == '__main__':
    main()
