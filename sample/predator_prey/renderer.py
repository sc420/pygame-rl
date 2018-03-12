#!/usr/bin/env python3
"""Sample: Use only the renderer with the default map.

Press the arrow keys to move agent 1. Press the "S" key to take the "STAND"
action of agent 1.

"""

# User-defined modules
import pygame_rl.scenario.predator_prey_environment as predator_prey_environment
import pygame_rl.scenario.predator_prey_renderer as predator_prey_renderer


def main():
    # Create a renderer options
    renderer_options = predator_prey_renderer.RendererOptions(
        show_display=True, max_fps=60, enable_key_events=True)

    # Create an environment
    env = predator_prey_environment.PredatorPreyEnvironment(
        renderer_options=renderer_options)

    # Get the renderer wrapped in the environment
    renderer = env.renderer

    # Initialize the renderer
    renderer.load()

    # Keep rendering until the renderer window is closed
    is_running = True
    while is_running:
        is_running = renderer.render()


if __name__ == '__main__':
    main()
