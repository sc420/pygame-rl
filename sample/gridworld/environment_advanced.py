#!/usr/bin/env python3
# pylint: disable=W0611
"""Sample: Interacting with the environment with advanced usage.
"""

# Native modules
import copy
import os

# Third-party modules
import gym
import numpy as np
import scipy.misc

# User-defined modules
import pygame_rl.scenario.gridworld
import pygame_rl.scenario.gridworld.options as options
import pygame_rl.scenario.gridworld.renderer as renderer
import pygame_rl.util.file_util as file_util


# Map size
MAP_SIZE = [9, 9]
# Action size
ACTION_SIZE = 5
# Group names and sizes
GROUP_NAMES = [
    'PLAYER1',
    'OBSTACLE1',
    'GOAL',
]
# Probability of random action
RANDOM_ACTION_PROB = 0.1


# Group sizes
group_sizes = []
# Reset counter
reset_counter = 0


def main():
    global group_sizes

    # Create an environment
    env = gym.make('gridworld-v1')

    # Resolve the map path relative to this file
    map_path = file_util.resolve_path(
        __file__, '../data/map/gridworld/gridworld_9x9.tmx')

    # Set the environment options
    env.env_options = options.GridworldOptions(
        map_path=map_path,
        action_space=gym.spaces.Discrete(ACTION_SIZE),
        step_callback=step_callback,
        reset_callback=reset_callback
    )

    env.renderer_options = renderer.RendererOptions(
        show_display=False, max_fps=60)

    # Load the enviornment
    env.load()

    # Set the random seed of the environment
    env.seed(0)

    # Run many episodes
    for episode_ind in range(6):
        # Print the episode number
        print('')
        print('Episode {}:'.format(episode_ind + 1))
        # Set the group names and sizes
        group_sizes = [
            1,
            episode_ind,
            1,
        ]
        env.env_options.set_group(GROUP_NAMES, group_sizes)
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
            # Transition to the next state
            state = next_state
            timestep += 1
        print('Episode ended. Reward: {}. Timestep: {}'.format(
            reward, timestep))

    # Save the last screenshot
    screenshot_relative_path = 'screenshot.png'
    screenshot_abs_path = os.path.abspath(screenshot_relative_path)
    scipy.misc.imsave(screenshot_abs_path, screenshot)
    print('The last screenshot is saved to {}'.format(screenshot_abs_path))


def step_callback(prev_state, action, random_state):
    state = copy.deepcopy(prev_state)
    # Get player 1 position
    pos = prev_state['PLAYER1'][0]
    # Get new position
    new_pos = get_new_pos(pos, action, random_state)
    # Update state
    if is_valid_pos(new_pos, prev_state):
        state['PLAYER1'][0] = new_pos
    done = is_done(pos, state)
    reward = 0.0
    info = {}
    return state, reward, done, info


def reset_callback(random_state):
    global reset_counter
    del random_state
    obstacles1 = np.asarray([
        np.array([4, 3]),
        np.array([3, 4]),
        np.array([4, 4]),
        np.array([5, 4]),
        np.array([4, 5]),
    ])
    reset_counter += 1
    return {
        'PLAYER1': np.asarray([
            np.array([0, 0]),
        ]),
        'OBSTACLE1': obstacles1[:(reset_counter - 1)],
        'GOAL': np.asarray([
            np.array([8, 8]),
        ]),
    }


def get_new_pos(pos, action, random_state):
    new_pos = np.array(pos)
    # Whether to choose random action
    if random_state.rand() < RANDOM_ACTION_PROB:
        action = random_state.randint(ACTION_SIZE)
    # Move the position
    if action == 0:  # Move right
        new_pos[0] += 1
    elif action == 1:  # Move up
        new_pos[1] -= 1
    elif action == 2:  # Move left
        new_pos[0] -= 1
    elif action == 3:  # Move down
        new_pos[1] += 1
    elif action == 4:  # Stand still
        pass
    else:
        raise ValueError('Unknown action: {}'.format(action))
    return new_pos


def is_valid_pos(pos, prev_state):
    in_bound = (pos[0] >= 0 and pos[0] < MAP_SIZE[0] and
                pos[1] >= 0 and pos[1] < MAP_SIZE[1])
    collision_group_names = [
        'OBSTACLE1',
    ]
    no_collision = not check_collision(
        pos, collision_group_names, prev_state)
    return in_bound and no_collision


def is_done(pos, state):
    collision_group_names = [
        'GOAL',
    ]
    return check_collision(pos, collision_group_names, state)


def check_collision(pos, collision_group_names, state):
    global group_sizes
    for group_index, group_name in enumerate(GROUP_NAMES):
        if not group_name in collision_group_names:
            continue
        for local_index in range(group_sizes[group_index]):
            other_pos = state[group_name][local_index]
            if np.array_equal(pos, other_pos):
                return True
    return False


if __name__ == '__main__':
    main()
