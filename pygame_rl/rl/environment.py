# Native modules
import abc


class Environment(metaclass=abc.ABCMeta):
    """The abstract class for the environment.
    """
    @abc.abstractmethod
    def reset(self):
        """Reset the environment and return the initial state.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def take_action(self, action):
        """Take an action from the agent and return the observation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def render(self):
        """Render the environment.
        """
        raise NotImplementedError()
