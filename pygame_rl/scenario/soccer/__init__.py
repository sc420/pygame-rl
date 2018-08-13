# Third-party modules
import gym.envs.registration as env_reg


# Register environments
env_reg.register(
    id='soccer-v0',
    entry_point='pygame_rl.scenario.soccer.envs:SoccerV0',
)
