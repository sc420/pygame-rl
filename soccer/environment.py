# Native modules
from abc import ABCMeta, abstractmethod


class Environment(metaclass=ABCMeta):
  """The abstract class for the enviornment.
  """
  @abstractmethod
  def reset(self):
    """Reset the environment and return the initial state.
    """
    raise NotImplementedError()

  @abstractmethod
  def take_action(self, action):
    """Take an action from the agent and return the observation.
    """
    raise NotImplementedError()

  @abstractmethod
  def render(self):
    """Render the environment.
    """
    raise NotImplementedError()
