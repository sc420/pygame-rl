# Third-party modules
import gym.envs.registration as env_reg


# Register environments
env_reg.register(
    id='gridworld-v0',
    entry_point='pygame_rl.scenario.gridworld.envs:GridworldV0',
)
env_reg.register(
    id='gridworld-v1',
    entry_point='pygame_rl.scenario.gridworld.envs:GridworldV1',
)
