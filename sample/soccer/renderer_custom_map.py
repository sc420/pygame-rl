#!/usr/bin/env python3
"""Sample: Use only the renderer with a custom map in "sample/data".

Press the arrow keys to move the agent 1. Press the "S" key to take the "STAND"
action of the agent 1.

"""

# User-defined modules
import pygame_rl.scenario.soccer_environment as soccer_environment
import pygame_rl.scenario.soccer_renderer as soccer_renderer
import pygame_rl.util.file_util as file_util


def main():
    # Resolve the map path relative to this file
    map_path = file_util.resolve_path(
        __file__, '../data/map/soccer/soccer_21x14_goal_6.tmx')

    # Create a soccer environment options
    env_options = soccer_environment.SoccerEnvironmentOptions(
        map_path=map_path, team_size=5, ai_frame_skip=2)

    # Create a renderer options
    renderer_options = soccer_renderer.RendererOptions(
        show_display=True, max_fps=60, enable_key_events=True)

    # Create a soccer environment
    soccer_env = soccer_environment.SoccerEnvironment(
        env_options, renderer_options=renderer_options)

    # Get the renderer wrapped in the environment
    renderer = soccer_env.renderer

    # Initialize the renderer
    renderer.load()

    # Keep rendering until the renderer window is closed
    is_running = True
    while is_running:
        is_running = renderer.render()


if __name__ == '__main__':
    main()
