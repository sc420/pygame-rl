#!/usr/bin/python

# User-defined modules
import soccer


def main():
  # Create an environment state
  env_state = soccer.EnvironmentState()

  # Create a renderer
  renderer = soccer.SoccerRenderer(env_state)
  # Initialize the renderer
  renderer.load()

  # Keep rendering until the renderer window is closed
  is_running = True
  while is_running:
    is_running = renderer.render()


if __name__ == '__main__':
  main()
