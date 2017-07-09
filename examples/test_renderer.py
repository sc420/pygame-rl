#!/usr/bin/python

# User-defined modules
import soccer


def main():
  # Create a soccer environment
  soccer_env = soccer.SoccerEnvironment()

  # Create a renderer
  renderer = soccer.SoccerRenderer(soccer_env, enable_key_events=True)

  # Initialize the renderer
  renderer.load()

  # Keep rendering until the renderer window is closed
  is_running = True
  while is_running:
    is_running = renderer.render()


if __name__ == '__main__':
  main()
