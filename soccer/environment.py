# Native modules
from abc import ABCMeta, abstractmethod


class Environment(metaclass=ABCMeta):
  """The abstract class for the enviornment.
  """
  @abstractmethod
  def reset(self):
    raise NotImplementedError()

  @abstractmethod
  def take_action(self, action):
    raise NotImplementedError()

  @abstractmethod
  def render(self):
    raise NotImplementedError()
