# Third-party modules
import numpy as np

# Project modules
from pygame_rl.scenario.soccer.actions import Actions
from pygame_rl.scenario.soccer.agent_modes import AgentModes
from pygame_rl.scenario.soccer.teams import Teams


class State(object):
    """The internal soccer state.
    """
    # Agent statuses as a list
    # * pos: Positions
    # * ball: Possession of the ball
    # * mode: Mode for the agent
    # * action: Last taken action for the agent
    # * frame_skip_index: Current frame skipping index, starting from 0,
    # resetting after it reaches the frame skip
    agent_list = []

    # Position to object index map
    pos_map = None

    # Time step
    time_step = 0

    # Soccer environment
    env = None

    # Soccer environment options
    env_options = None

    # Map data
    map_data = None

    # Random state
    random_state = None

    def __init__(self, env, env_options, map_data, random_state):
        self.env = env
        self.env_options = env_options
        self.map_data = map_data
        self.random_state = random_state
        self.reset()

    def update_random_state(self, random_state):
        self.random_state = random_state

    def reset(self):
        # Initialize the agent list
        self._reset_agent_list()
        # Reset position map
        self._reset_pos_map()
        # Randomize the agent statuses
        self.randomize()
        # Initialize the time step
        self.time_step = 0

    def randomize(self):
        # Choose a random agent in a random team to possess the ball
        rand_idx = self.random_state.randint(len(Teams))
        team_has_ball = Teams(rand_idx)
        team_agent_has_ball = self.random_state.randint(
            self.env_options.team_size)
        # Set the properties for each team and each agent
        for team_name in Teams:
            for team_agent_index in range(self.env_options.team_size):
                # Get the agent index
                agent_index = self.env.get_agent_index(
                    team_name, team_agent_index)
                # Randomize the agent positions
                found_pos = False
                while not found_pos:
                    spawn_list = self.map_data.spawn[team_name.name]
                    rand_idx = self.random_state.randint(len(spawn_list))
                    agent_pos = spawn_list[rand_idx]
                    if not self.get_pos_status(agent_pos):
                        self.set_agent_pos(agent_index, agent_pos)
                        found_pos = True
                # Randomize the possession of the ball
                set_ball = (team_name == team_has_ball
                            and team_agent_index == team_agent_has_ball)
                if set_ball:
                    self.set_agent_ball(agent_index, True)
                else:
                    self.set_agent_ball(agent_index, False)
                # Randomize the agent mode
                rand_idx = self.random_state.randint(len(AgentModes))
                agent_mode = AgentModes(rand_idx)
                self.set_agent_mode(agent_index, agent_mode)
                # Reset the action
                self.set_agent_action(agent_index, Actions.STAND)

    def is_terminal(self):
        # When the time step exceeds 100
        if self.time_step >= 100:
            return True
        # When one of the agent reaches the goal
        for agent_index in range(self.env_options.agent_size):
            if self.is_agent_win(agent_index):
                return True
        # Otherwise, the state isn't terminal
        return False

    def is_team_win(self, team_name):
        for team_agent_index in range(self.env_options.team_size):
            agent_index = self.env.get_agent_index(team_name, team_agent_index)
            if self.is_agent_win(agent_index):
                return True
        return False

    def is_agent_win(self, agent_index):
        # Get the agent statuses
        agent_pos = self.get_agent_pos(agent_index)
        has_ball = self.get_agent_ball(agent_index)
        # Agent cannot win if he doesn't possess the ball
        if not has_ball:
            return False
        # Get the team name
        team_name = Teams(agent_index)
        # Check whether the position is in the goal area
        return agent_pos in self.map_data.goals[team_name.name]

    def get_gym_state(self, map_size):
        agent_size = len(self.agent_list)
        player_goal_size = len(self.map_data.goals['PLAYER'])
        computer_goal_size = len(self.map_data.goals['COMPUTER'])
        map_2d = np.zeros(map_size)
        agent_pos_list = np.zeros((agent_size, 2))
        rel_player_goals = np.zeros((agent_size, player_goal_size, 2))
        rel_computer_goals = np.zeros((agent_size, computer_goal_size, 2))
        rel_other_agent_pos = np.zeros((agent_size, agent_size - 1, 2))
        ball_list = np.zeros(agent_size)
        mode_list = np.zeros(agent_size)
        action_list = np.zeros(agent_size)
        for pos in self.map_data.walkable:
            # Walkable
            map_2d[tuple(pos)] = 1
        for pos in self.map_data.goals['PLAYER']:
            # Player goal
            map_2d[tuple(pos)] = 2
        for pos in self.map_data.goals['COMPUTER']:
            # Computer goal
            map_2d[tuple(pos)] = 3
        for idx, agent in enumerate(self.agent_list):
            # Agent
            ball_list[idx] = self.get_agent_ball(idx)
            mode_list[idx] = self.get_agent_mode(idx)
            action_list[idx] = self.get_agent_action(idx)
            # Agent position
            agent_pos = agent['pos']
            agent_pos_list[idx, :] = agent_pos
            # Other agent positions
            for other_idx, other_agent in enumerate(self.agent_list):
                if idx != other_idx:
                    other_agent_pos = other_agent['pos']
                    rel_other_agent_pos[idx, :] = self.get_rel_pos(
                        agent_pos, other_agent_pos)
            # Relative goal positions
            for pos_idx, goal in enumerate(self.map_data.goals['PLAYER']):
                rel_player_goals[idx, pos_idx, :] = self.get_rel_pos(
                    agent_pos, goal)
            for pos_idx, goal in enumerate(self.map_data.goals['COMPUTER']):
                rel_computer_goals[idx, pos_idx, :] = self.get_rel_pos(
                    agent_pos, goal)
        return {
            'map': map_2d,
            'agent_pos': agent_pos_list,
            'relative': {
                'player_goals': rel_player_goals,
                'computer_goals': rel_computer_goals,
                'other_agent_pos': rel_other_agent_pos,
            },
            'ball': ball_list,
            'mode': mode_list,
            'action': action_list,
        }

    def get_agent_pos(self, agent_index):
        return self.agent_list[agent_index]['pos']

    def set_agent_pos(self, agent_index, pos):
        # Get old position
        old_pos = self.agent_list[agent_index].get('pos', None)
        # Remove old position from map
        if old_pos:
            old_pos_tuple = tuple(old_pos)
            self.pos_map.pop(old_pos_tuple, None)
        # Set position in map
        if pos:
            pos_tuple = tuple(pos)
            self.pos_map[pos_tuple] = agent_index
        # Set the new position
        self.agent_list[agent_index]['pos'] = pos

    def get_agent_ball(self, agent_index):
        return self.agent_list[agent_index]['ball']

    def set_agent_ball(self, agent_index, has_ball):
        self.agent_list[agent_index]['ball'] = has_ball

    def get_agent_mode(self, agent_index):
        return self.agent_list[agent_index]['mode']

    def set_agent_mode(self, agent_index, mode):
        self.agent_list[agent_index]['mode'] = mode

    def get_agent_action(self, agent_index):
        return self.agent_list[agent_index]['action']

    def set_agent_action(self, agent_index, action):
        self.agent_list[agent_index]['action'] = action

    def get_agent_frame_skip_index(self, agent_index):
        return self.agent_list[agent_index]['frame_skip_index']

    def set_agent_frame_skip_index(self, agent_index, frame_skip_index):
        self.agent_list[agent_index]['frame_skip_index'] = frame_skip_index

    def get_pos_status(self, pos):
        pos_tuple = tuple(pos)
        agent_index = self.pos_map.get(pos_tuple, None)
        if agent_index:
            team_name = Teams(agent_index)
            team_agent_index = self.env.get_team_agent_index(agent_index)
            return {
                'team_name': team_name,
                'team_agent_index': team_agent_index,
                'agent_index': agent_index,
            }
        else:
            return None

    def get_ball_possession(self):
        for team_name in Teams:
            for team_agent_index in range(self.env_options.team_size):
                agent_index = self.env.get_agent_index(
                    team_name, team_agent_index)
                if self.get_agent_ball(agent_index):
                    return {
                        'team_name': team_name,
                        'team_agent_index': team_agent_index,
                        'agent_index': agent_index,
                    }
        return None

    def switch_ball(self, agent_index, other_agent_index):
        agent_ball = self.get_agent_ball(agent_index)
        self.set_agent_ball(agent_index, not agent_ball)
        self.set_agent_ball(other_agent_index, agent_ball)

    def increase_frame_skip_index(self, agent_index, frame_skip):
        old_frame_skip_index = self.agent_list[agent_index]['frame_skip_index']
        new_frame_skip_index = (old_frame_skip_index + 1) % frame_skip
        self.agent_list[agent_index]['frame_skip_index'] = new_frame_skip_index

    def increase_time_step(self):
        self.time_step += 1

    @staticmethod
    def get_rel_pos(ref, target):
        return [target[0] - ref[0], target[1] - ref[1]]

    def _reset_agent_list(self):
        self.agent_list = [{}
                           for _ in range(self.env_options.agent_size)]
        for agent_index in range(self.env_options.agent_size):
            self.set_agent_pos(agent_index, None)
            self.set_agent_ball(agent_index, False)
            self.set_agent_mode(agent_index, None)
            self.set_agent_action(agent_index, None)
            self.set_agent_frame_skip_index(agent_index, 0)

    def _reset_pos_map(self):
        self.pos_map = {}

    def __repr__(self):
        message = ''
        # The agent positions, mode, and last taken action
        for team_index, team in enumerate(Teams):
            if team_index > 0:
                message += '\n'
            message += 'Team {}:'.format(team.name)
            for team_agent_index in range(self.env_options.team_size):
                # Get the agent index
                agent_index = self.env.get_agent_index(team, team_agent_index)
                # Get the position
                agent_pos = self.get_agent_pos(agent_index)
                # Get the mode
                agent_mode = self.get_agent_mode(agent_index)
                # Get the last taken action
                agent_action = self.get_agent_action(agent_index)
                message += '\nAgent {}:'.format(team_agent_index + 1)
                message += ' Position: {}'.format(agent_pos)
                if agent_mode is not None:
                    message += ', Mode: {}'.format(agent_mode.name)
                if agent_action is not None:
                    message += ', Action: {}'.format(agent_action.name)
        # The possession of the ball
        ball_possession = self.get_ball_possession()
        team = ball_possession['team_name']
        team_agent_index = ball_possession['team_agent_index']
        message += '\nBall possession: In team {} with agent {}'.format(
            team.name, team_agent_index + 1)
        # The time step
        message += '\nTime step: {}'.format(self.time_step)
        return message

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.agent_list == other.agent_list
                and self.time_step == other.time_step)

    def __hash__(self):
        hash_list = []
        for agent_index in range(self.env_options.agent_size):
            hash_list.extend(self.get_agent_pos(agent_index))
            hash_list.append(self.get_agent_ball(agent_index))
            hash_list.append(self.get_agent_mode(agent_index))
            hash_list.append(self.get_agent_action(agent_index))
        hash_list.append(self.time_step)
        return hash(tuple(hash_list))
