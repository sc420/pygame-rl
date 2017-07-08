#!/usr/bin/python

# User-defined modules
from environment import EnvironmentState
from renderer import Soccer


def main():
  # Create an environment state
  env_state = EnvironmentState()

  # Create a renderer environment
  soccer = Soccer(env_state)
  # Initialize the renderer environment
  soccer.load()

  # Keep rendering until the renderer window is closed
  is_running = True
  while is_running:
    is_running = soccer.render()


if __name__ == '__main__':
  main()
