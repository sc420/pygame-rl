#!/usr/bin/python

# User-defined modules
import soccer


def main():
  # Create a renderer options
  renderer_options = soccer.RendererOptions(
      show_display=True, max_fps=60, enable_key_events=True)

  # Create a soccer environment
  soccer_env = soccer.SoccerEnvironment(renderer_options)

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
