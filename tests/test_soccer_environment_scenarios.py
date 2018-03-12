# Native modules
import random

# Third-party modules
import pytest

# Testing targets
import pygame_rl.scenario.soccer_environment as soccer_environment


class SoccerEnvironmentTest(object):
    env = None
    state = None
    player_index = None
    computer_index = None

    @classmethod
    def setup_class(cls):
        # Initialize the environment
        env_options = soccer_environment.SoccerEnvironmentOptions(team_size=2)
        cls.env = soccer_environment.SoccerEnvironment(env_options=env_options)
        # Get the environment state
        cls.state = cls.env.state
        # Get the agent indexes
        cls.player_index = [cls.env.get_agent_index('PLAYER', team_index)
                            for team_index in range(2)]
        cls.computer_index = [cls.env.get_agent_index('COMPUTER', team_index)
                              for team_index in range(2)]

    @pytest.mark.parametrize('seed', range(100))
    def test_adjacent(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [6, 0])
        self.state.set_agent_pos(self.player_index[1], [6, 1])
        self.state.set_agent_pos(self.computer_index[0], [7, 0])
        self.state.set_agent_pos(self.computer_index[1], [7, 1])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
        # Give the ball to player 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.player_index[0])
        # Take the action
        self.env.take_cached_action(self.player_index[0], 'STAND')
        # Update the state
        self.env.update_state()
        # Player 1 position should have not changed
        assert self.state.get_agent_pos(self.player_index[0]) == [6, 0]
        # Player 2 position should have either not changed or moved, but not up
        possible_pos = [[6, 1], [5, 1], [6, 2], [7, 1]]
        assert self.state.get_agent_pos(self.player_index[1]) in possible_pos
        # Computer 1 positions should have either not changed or swapped with
        # computer 2
        possible_pos = [[7, 0], [7, 1]]
        assert self.state.get_agent_pos(self.computer_index[0]) in possible_pos
        # Computer 2 positions should have either not changed, swapped with
        # computer 1, or swapped with player 2
        possible_pos = [[7, 0], [7, 1], [6, 1]]
        assert self.state.get_agent_pos(self.computer_index[1]) in possible_pos
        # Computer 2 can't have the ball
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        assert ball_agent_index != self.computer_index[1]

    @pytest.mark.parametrize('seed', range(100))
    def test_avoid_opponent(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [1, 2])
        self.state.set_agent_pos(self.player_index[1], [1, 3])
        self.state.set_agent_pos(self.computer_index[0], [7, 2])
        self.state.set_agent_pos(self.computer_index[1], [7, 3])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'DEFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'DEFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'DEFENSIVE')
        # Give the ball to computer 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.computer_index[0])
        # Take the action
        self.env.take_cached_action(self.player_index[0], 'MOVE_RIGHT')
        # Update the state
        self.env.update_state()
        # Player 2 should approach the nearest opponent goal position against
        # computer 1
        possible_pos = [[1, 2], [0, 3]]
        assert self.state.get_agent_pos(self.player_index[1]) in possible_pos
        # Computer 1 should avoid player 1
        assert self.state.get_agent_pos(self.computer_index[0]) == [8, 2]
        # Computer 2 should approach the nearest opponent goal position against
        # player 2
        assert self.state.get_agent_pos(self.computer_index[1]) == [8, 3]

    @pytest.mark.parametrize('seed', range(100))
    def test_advance_to_goal(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [1, 2])
        self.state.set_agent_pos(self.player_index[1], [1, 3])
        self.state.set_agent_pos(self.computer_index[0], [7, 2])
        self.state.set_agent_pos(self.computer_index[1], [7, 3])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
        # Give the ball to computer 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.computer_index[0])
        # Take the action
        self.env.take_cached_action(self.player_index[0], 'MOVE_RIGHT')
        # Update the state
        self.env.update_state()
        # Player 2 should intercept against computer 1
        assert self.state.get_agent_pos(self.player_index[1]) == [2, 3]
        # Computer 1 should approach the furthest goal position against player 1
        assert self.state.get_agent_pos(self.computer_index[0]) == [6, 2]
        # Computer 2 should intercept against player 2
        assert self.state.get_agent_pos(self.computer_index[1]) == [6, 3]

    @pytest.mark.parametrize('seed', range(100))
    def test_defend_goal(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [1, 2])
        self.state.set_agent_pos(self.player_index[1], [1, 3])
        self.state.set_agent_pos(self.computer_index[0], [7, 2])
        self.state.set_agent_pos(self.computer_index[1], [7, 3])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'DEFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'DEFENSIVE')
        # Give the ball to player 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.player_index[0])
        # Take the action
        self.env.take_cached_action(self.player_index[0], 'MOVE_RIGHT')
        # Update the state
        self.env.update_state()
        # Player 2 should intercept against computer 1
        assert self.state.get_agent_pos(self.player_index[1]) == [2, 3]
        # Computer 1 should approach the nearest opponent goal position against
        # player 1
        assert self.state.get_agent_pos(self.computer_index[0]) == [8, 2]
        # Computer 2 should approach the nearest opponent goal position against
        # player 1
        possible_pos = [[7, 2], [8, 3]]
        assert self.state.get_agent_pos(self.computer_index[1]) in possible_pos

    @pytest.mark.parametrize('seed', range(100))
    def test_intercept_goal(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [1, 2])
        self.state.set_agent_pos(self.player_index[1], [1, 3])
        self.state.set_agent_pos(self.computer_index[0], [7, 2])
        self.state.set_agent_pos(self.computer_index[1], [7, 3])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'DEFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
        # Give the ball to player 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.player_index[0])
        # Take the action
        self.env.take_cached_action(self.player_index[0], 'MOVE_RIGHT')
        # Update the state
        self.env.update_state()
        # Player 2 should approach the nearest opponent goal position against
        # computer 1
        assert self.state.get_agent_pos(self.player_index[1]) == [0, 3]
        # Computer 1 should intercept against player 1
        assert self.state.get_agent_pos(self.computer_index[0]) == [6, 2]
        # Computer 2 should intercept against player 1
        assert self.state.get_agent_pos(self.computer_index[1]) == [6, 3]

    @pytest.mark.parametrize('seed', range(100))
    def test_negative_reward(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [1, 2])
        self.state.set_agent_pos(self.player_index[1], [7, 0])
        self.state.set_agent_pos(self.computer_index[0], [3, 2])
        self.state.set_agent_pos(self.computer_index[1], [3, 3])
        # Set the agent modes
        self.state.set_agent_mode(self.player_index[1], 'DEFENSIVE')
        self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
        # Give the ball to player 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.player_index[0])
        # The computer agent should score in 100 steps
        for _ in range(100):
            # Take the action
            self.env.take_cached_action(self.player_index[0], 'STAND')
            # Update the state and get the observation
            observation = self.env.update_state()
            # Teleport player 2 to the original position so that he can't never
            # catch the ball
            self.state.set_agent_pos(self.player_index[1], [7, 0])
            if observation.next_state.is_team_win('COMPUTER'):
                break
        assert observation.reward == pytest.approx(-1.0)

    @pytest.mark.parametrize('seed', range(100))
    def test_positive_reward(self, seed):
        # Set the random seed
        random.seed(seed)
        # Set the initial positions
        self.state.set_agent_pos(self.player_index[0], [5, 2])
        self.state.set_agent_pos(self.player_index[1], [5, 3])
        self.state.set_agent_pos(self.computer_index[0], [3, 2])
        self.state.set_agent_pos(self.computer_index[1], [3, 3])
        # Set the computer agent modes
        self.state.set_agent_mode(self.computer_index[0], 'OFFENSIVE')
        self.state.set_agent_mode(self.computer_index[1], 'OFFENSIVE')
        # Give the ball to player 1
        ball_possession = self.state.get_ball_possession()
        ball_agent_index = ball_possession['agent_index']
        self.state.switch_ball(ball_agent_index, self.player_index[0])
        # The player agent should score in exactly 3 steps
        for _ in range(3):
            # Take the action
            self.env.take_cached_action(self.player_index[0], 'MOVE_RIGHT')
            # Update the state
            observation = self.env.update_state()
        assert observation.next_state.is_team_win('PLAYER')
        assert observation.reward == pytest.approx(1.0)
