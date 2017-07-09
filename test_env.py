#!/usr/bin/python

# Native modules
import random

# User-defined modules
import soccer


def main():
  # Initialize the random number generator
  random.seed(0)

  # Create a soccer environment
  soccer_env = soccer.SoccerEnvironment()

  for episode_ind in range(10):
    print('')
    print('Episode {}:'.format(episode_ind + 1))
    observation = soccer_env.reset()
    print('Initial state:\n{}'.format(observation))
    for time_step_ind in range(1000):
      soccer_env.render()
      action = random.choice(soccer_env.actions)
      observation = soccer_env.take_action(action)
      if soccer_env.state.is_terminal():
        print('Episode {} ends at time step {}'.format(
            episode_ind + 1, time_step_ind + 1))
        break


if __name__ == '__main__':
  main()
