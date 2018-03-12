# Third-party modules
import gym.envs.registration as env_reg


# Register environments
env_reg.register(
    id='gym-walkr-v0',
    entry_point='pygame_rl.scenario.gridworld.envs:GridworldV0',
)
