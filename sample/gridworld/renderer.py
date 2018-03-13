#!/usr/bin/env python3
"""Sample: Use only the renderer with the default map.

Press the arrow keys to move agent 1. Press the "S" key to take the "STAND"
action of agent 1.

"""

# Third-party modules
import gym

# User-defined modules
import pygame_rl.scenario.gridworld.renderer as renderer


def main():
    # Create an environment
    env = gym.make('gridworld-v0')

    # Set the renderer options
    env.renderer_options = renderer.RendererOptions(
        show_display=True, max_fps=60, enable_key_events=True)

    # Reset the environment
    env.reset()

    # Keep rendering until the renderer window is closed
    is_running = True
    while is_running:
        is_running = env.renderer.render()


if __name__ == '__main__':
    main()
