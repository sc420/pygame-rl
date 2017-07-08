#!/usr/bin/python

# User-defined modules
from renderer import Soccer


def main():
  # Create a renderer environment
  soccer = Soccer()
  # Initialize the renderer environment
  soccer.init()
  # Keep rendering until the renderer window is closed
  is_running = True
  while is_running:
    is_running = soccer.render()


if __name__ == '__main__':
  main()
