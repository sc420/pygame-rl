# Third-party modules
import gym
import numpy as np

# Project modules
from pygame_rl.scenario.soccer.actions import Actions
from pygame_rl.scenario.soccer.agent_modes import AgentModes
from pygame_rl.scenario.soccer.ai_modes import AiModes
from pygame_rl.scenario.soccer.map_data import MapData
from pygame_rl.scenario.soccer.options import Options
from pygame_rl.scenario.soccer.renderer import Renderer
from pygame_rl.scenario.soccer.state import State
from pygame_rl.scenario.soccer.teams import Teams


class SoccerV0(gym.Env):
    """Soccer environment following OpenAI Gym API.
    """
    ### Gym Attributes ###

    # Metadata
    metadata = {'render.modes': ['rgb_array']}
    # Observation space
    observation_space = None
    # Action space
    action_space = None

    ### Environment Attributes ###

    # Environment options
    options = None
    # Renderer options
    renderer_options = None
    # Map data
    map_data = None
    # Renderer
    renderer = None

    ### State ###

    # State
    state = None
    # Numpy random state
    random_state = None
    # Cached action
    cached_action = None
    # Lazy loading of renderer
    renderer_loaded = False

    ### Gym Methods ###

    def seed(self, seed=None):
        self.random_state = np.random.RandomState(seed)
        self.state.update_random_state(self.random_state)
        return self.random_state

    def step(self, action):
        # Cache the actions
        self.cached_action = action
        # Update agent actions
        self._update_agent_actions()
        # Get the intended positions
        intended_pos = self._get_intended_pos(self.cached_action)
        # Update the agent positions
        self._update_agent_pos(intended_pos)
        # Update taken actions
        self._update_taken_actions()
        # Update frame skipping index
        self._update_frame_skip_index()
        # Update time step
        self._update_time_step()
        # Get the reward
        reward = self._get_reward()
        # Check terminal
        done = self.state.is_terminal()
        # Return the state, reward, done, and info
        gym_state = self._gym_state()
        return gym_state, reward, done, {}

    def reset(self):
        self.state.reset()
        # Return the state
        gym_state = self._gym_state()
        return gym_state

    def render(self, mode='rgb_array'):
        # Lazy load the renderer
        if not self.renderer_loaded:
            self.renderer.load()
            self.renderer_loaded = True
        # Render
        self.renderer.render()
        # Return renderer screenshot
        return self.renderer.get_screenshot()

    ### Initialization Methods ###

    def __init__(self):
        # Use default random state
        self.random_state = np.random.RandomState(0)

    def load(self):
        # Save or create environment options
        self.options = self.options or Options()
        # Load map data
        self.map_data = MapData(self.options.map_path)
        # Initialize the state
        self.state = State(self, self.options,
                           self.map_data, self.random_state)
        # Initialize renderer
        self.renderer = Renderer(
            self.options.map_path, self, self.renderer_options)
        # Initialize observation space
        self._init_obs_space()
        # Initialize action space
        self._init_action_space()

    def _init_obs_space(self):
        map_size = self.map_data.map_size
        map_len = np.prod(map_size)
        agent_size = len(Teams) * self.options.team_size
        player_goal_size = len(self.map_data.goals['PLAYER'])
        computer_goal_size = len(self.map_data.goals['COMPUTER'])
        low_map_bound = [-map_size[0] + 1, -map_size[0] + 1]
        high_map_bound = [map_size[0] - 1, map_size[1] - 1]
        # Map, agent positions, relative player goals, relative computer goals,
        # other agent positions, ball possessions, modes, actions
        low = map_len * [0] + \
            agent_size * [0, 0] + \
            agent_size * player_goal_size * low_map_bound + \
            agent_size * computer_goal_size * low_map_bound + \
            agent_size * (agent_size - 1) * low_map_bound + \
            agent_size * [0] + \
            agent_size * [0] + \
            agent_size * [0]
        high = map_len * [3] + \
            agent_size * high_map_bound + \
            agent_size * player_goal_size * high_map_bound + \
            agent_size * computer_goal_size * high_map_bound + \
            agent_size * (agent_size - 1) * high_map_bound + \
            agent_size * [1] + \
            agent_size * [len(AgentModes) - 1] + \
            agent_size * [len(Actions) - 1]
        self.observation_space = gym.spaces.Box(
            low=np.array(low), high=np.array(high), dtype=np.uint8)

    def _init_action_space(self):
        agent_size = len(Teams) * self.options.team_size
        nvec = [len(Actions)] * agent_size
        self.action_space = gym.spaces.MultiDiscrete(nvec)

    def _gym_state(self):
        map_size = self.map_data.map_size
        state = self.state.get_gym_state(map_size)
        return state

    def _update_agent_actions(self):
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                # Skip and update if the cached action has been specified
                agent_action = self.cached_action[agent_index]
                if agent_action != Actions.NOOP:
                    self.cached_action[agent_index] = Actions(agent_action)
                    continue
                # Select the previous action if it's frame skipping
                if self.state.get_agent_frame_skip_index(agent_index) > 0:
                    action = self.state.get_agent_action(agent_index)
                else:
                    action = self._get_ai_action(team_name, team_agent_index)
                # Update the cached action
                self.cached_action[agent_index] = action

    def get_agent_index(self, team_name, team_agent_index):
        # Map the team name to the group index
        if team_name == Teams.PLAYER:
            group_index = 0
        elif team_name == Teams.COMPUTER:
            group_index = 1
        else:
            raise KeyError('Unknown team name {}'.format(team_name))
        # Calculate the agent index
        return self.options.team_size * group_index + team_agent_index

    def get_opponent_team_name(self, team_name):
        if team_name == Teams.PLAYER:
            return Teams.COMPUTER
        elif team_name == Teams.COMPUTER:
            return Teams.PLAYER
        else:
            raise KeyError('Unknown team name {}'.format(team_name))

    def get_team_agent_index(self, agent_index):
        return agent_index % self.options.team_size

    def _init_cached_action(self):
        self.cached_action = {}
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                self.cached_action[agent_index] = None

    def _get_agent_actions(self, player_action):
        # Build a dict of the agent index to the actions
        actions = {}
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                # Choose the action by the team and agent index
                if team_name == Teams.PLAYER:
                    if team_agent_index <= 0:
                        # The action only takes effect on the first agent in the
                        # team
                        agent_action = player_action
                    else:
                        # The collaborators have the same AI as the opponents
                        agent_action = self._get_ai_action(
                            team_name, team_agent_index)
                elif team_name == Teams.COMPUTER:
                    agent_action = self._get_ai_action(
                        team_name, team_agent_index)
                else:
                    raise KeyError('Unknown team name {}'.format(team_name))
                actions[agent_index] = agent_action
        return actions

    def _get_walkable_moved_pos(self, pos, action):
        # Get the moved position
        moved_pos = self.get_moved_pos(pos, action)
        # Use the moved position if it's in the walkable area
        if moved_pos in self.map_data.walkable:
            return moved_pos
        else:
            return pos

    def _update_agent_pos(self, intended_pos):
        # Detect the overlapping positions and switch the ball
        detecting_overlap = True
        has_switched = False
        while detecting_overlap:
            # Get the overlapping position to agent index mapping
            overlapping_pos_to_agent = self._get_overlapping_pos_to_agent(
                intended_pos)
            # Update the positions
            detecting_overlap = False
            for (_, agent_index_list) in overlapping_pos_to_agent.items():
                if len(agent_index_list) > 1:
                    # Update the ball possession only once
                    if not has_switched:
                        switch = self._update_ball_possession(agent_index_list)
                        has_switched = has_switched or switch
                    # Use the old positions
                    for agent_index in agent_index_list:
                        intended_pos[agent_index] = self.state.get_agent_pos(
                            agent_index)
                    # Indicate the process should continue
                    detecting_overlap = True
        # Update the non-overlapping positions
        for (agent_index, pos) in intended_pos.items():
            self.state.set_agent_pos(agent_index, pos)

    def _update_taken_actions(self):
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                action = self.cached_action[agent_index]
                self.state.set_agent_action(agent_index, action)

    def _update_frame_skip_index(self):
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                self.state.increase_frame_skip_index(
                    agent_index, self.options.ai_frame_skip)

    def _update_time_step(self):
        self.state.increase_time_step()

    def _update_ball_possession(self, agent_index_list):
        # Get the ball possessions of the agents
        has_ball_agent_index = None
        no_ball_agent_list = []
        for agent_index in agent_index_list:
            has_ball = self.state.get_agent_ball(agent_index)
            if has_ball:
                has_ball_agent_index = agent_index
            else:
                no_ball_agent_list.append(agent_index)
        # Only switch the ball possession when one agent has the ball in the
        # list
        if not has_ball_agent_index is None:
            # Randomly switch the ball
            rand_idx = self.random_state.randint(len(no_ball_agent_list))
            switch_agent_index = no_ball_agent_list[rand_idx]
            self.state.switch_ball(has_ball_agent_index, switch_agent_index)
            # Indicate the switching has occurred
            return True
        # Indicate no switch
        return False

    def _get_intended_pos(self, actions):
        # Build a dict of the agent index to the intended moved position
        intended_pos = {}
        for team_name in Teams:
            for team_agent_index in range(self.options.team_size):
                agent_index = self.get_agent_index(team_name, team_agent_index)
                # Get the action
                action = actions[agent_index]
                # Get the original position
                pos = self.state.get_agent_pos(agent_index)
                # Save the walkable position
                intended_pos[agent_index] = self._get_walkable_moved_pos(
                    pos, action)
        return intended_pos

    def _get_ai_action(self, team_name, team_agent_index):
        # Get the opponent team name
        opponent_team_name = self.get_opponent_team_name(team_name)
        # Get the agent info
        agent_index = self.get_agent_index(team_name, team_agent_index)
        agent_pos = self.state.get_agent_pos(agent_index)
        agent_ball = self.state.get_agent_ball(agent_index)
        agent_mode = self.state.get_agent_mode(agent_index)
        agent_frame_skip_index = self.state.get_agent_frame_skip_index(
            agent_index)
        # Select the previous action if it's frame skipping
        if agent_frame_skip_index > 0:
            return self.state.get_agent_action(agent_index)
        # Get the position of the nearest opponent
        nearest_opponent_index = self._get_nearest_opponent_index(
            team_name, team_agent_index)
        nearest_opponent_pos = self.state.get_agent_pos(nearest_opponent_index)
        # Get the position of the defensive target
        defensive_target_agent_index = self._get_defensive_agent_index(
            team_name, team_agent_index)
        defensive_target_agent_pos = self.state.get_agent_pos(
            defensive_target_agent_index)
        # Calculate the target position and the strategic mode
        if agent_mode == AgentModes.DEFENSIVE:
            if agent_ball:
                target_pos = nearest_opponent_pos
                strategic_mode = AiModes.AVOID
            else:
                # Calculate the distance from the agent
                goals = self.map_data.goals[opponent_team_name.name]
                distances = [self.get_pos_distance(goal_pos,
                                                   defensive_target_agent_pos)
                             for goal_pos in goals]
                # Select the minimum distance
                min_distance_index = np.argmin(distances)
                target_pos = goals[min_distance_index]
                strategic_mode = AiModes.APPROACH
        elif agent_mode == AgentModes.OFFENSIVE:
            if agent_ball:
                # Calculate the distance from the opponent
                goals = self.map_data.goals[team_name.name]
                distances = [self.get_pos_distance(goal_pos,
                                                   nearest_opponent_pos)
                             for goal_pos in goals]
                # Select the maximum distance
                max_distance_index = np.argmax(distances)
                target_pos = goals[max_distance_index]
                strategic_mode = AiModes.APPROACH
            else:
                target_pos = defensive_target_agent_pos
                strategic_mode = AiModes.INTERCEPT
        else:
            raise KeyError('Unknown agent mode {}'.format(agent_mode))
        # Get the strategic action
        action = self._get_strategic_action(
            agent_pos, target_pos, strategic_mode)
        return action

    def _get_nearest_opponent_index(self, team_name, team_agent_index):
        # Get the opponent team name
        opponent_team_name = self.get_opponent_team_name(team_name)
        # Get the agent position
        agent_index = self.get_agent_index(team_name, team_agent_index)
        agent_pos = self.state.get_agent_pos(agent_index)
        # Find the nearest opponent position
        nearest_opponent_index = None
        nearest_dist = np.inf
        for opponent_team_agent_index in range(self.options.team_size):
            opponent_index = self.get_agent_index(
                opponent_team_name, opponent_team_agent_index)
            opponent_pos = self.state.get_agent_pos(opponent_index)
            # Calculate the distance
            dist = self.get_pos_distance(agent_pos, opponent_pos)
            if dist < nearest_dist:
                nearest_opponent_index = opponent_index
                nearest_dist = dist
        return nearest_opponent_index

    def _get_defensive_agent_index(self, team_name, team_agent_index):
        # Get the ball possession status
        ball_possession = self.state.get_ball_possession()
        has_ball_agent_index = ball_possession['agent_index']
        has_ball_team_name = ball_possession['team_name']
        if has_ball_team_name != team_name:
            # Defend the opponent who possesses the ball
            return has_ball_agent_index
        else:
            # Defend the nearest opponent
            return self._get_nearest_opponent_index(team_name, team_agent_index)

    def _get_strategic_action(self, source_pos, target_pos, mode):
        # Calculate the original Euclidean distance
        orig_dist = self.get_pos_distance(source_pos, target_pos)
        # Find the best action
        rand_idx = self.random_state.randint(len(Actions) - 1)
        best_action = Actions(rand_idx + 1)
        best_dist = orig_dist
        # Shuffle the actions except NOOP
        rand_idxs = self.random_state.choice(
            len(Actions) - 1, len(Actions) - 1, replace=False)
        shuffled_actions = [Actions(i + 1) for i in rand_idxs]
        # Find the best action
        for action in shuffled_actions:
            # Get the moved position after doing the action
            moved_pos = self.get_moved_pos(source_pos, action)
            # Check whether the moved position is walkable
            if not moved_pos in self.map_data.walkable:
                continue
            # Calculate the new Euclidean distance
            moved_dist = self.get_pos_distance(moved_pos, target_pos)
            if mode == AiModes.APPROACH:
                if moved_dist < best_dist:
                    best_action = action
                    best_dist = moved_dist
            elif mode == AiModes.AVOID:
                if moved_dist > best_dist:
                    best_action = action
                    best_dist = moved_dist
            elif mode == AiModes.INTERCEPT:
                if moved_dist < best_dist and moved_dist >= 1.0:
                    best_action = action
                    best_dist = moved_dist
            else:
                raise KeyError('Unknown mode {}'.format(mode))
        return best_action

    def _get_overlapping_pos_to_agent(self, intended_pos):
        overlapping_pos_to_agent = {}
        for (agent_index, pos) in intended_pos.items():
            # Use the old position if the new position is not walkable
            if not pos in self.map_data.walkable:
                pos = self.state.get_agent_pos(agent_index)
            # Use the tuple as the key
            pos_tuple = tuple(pos)
            if pos_tuple in overlapping_pos_to_agent:
                overlapping_pos_to_agent[pos_tuple].append(agent_index)
            else:
                overlapping_pos_to_agent[pos_tuple] = [agent_index]
        return overlapping_pos_to_agent

    def _get_reward(self):
        if self.state.is_team_win(Teams.PLAYER):
            return 1.0
        elif self.state.is_team_win(Teams.COMPUTER):
            return -1.0
        else:
            return 0.0

    @staticmethod
    def get_moved_pos(pos, action):
        # Copy the position
        pos = list(pos)
        # Move to the 4-direction grid
        if action == Actions.MOVE_RIGHT:
            pos[0] += 1
        elif action == Actions.MOVE_UP:
            pos[1] -= 1
        elif action == Actions.MOVE_LEFT:
            pos[0] -= 1
        elif action == Actions.MOVE_DOWN:
            pos[1] += 1
        elif action == Actions.STAND:
            pass
        else:
            raise KeyError('Unknown action {}'.format(action))
        return pos

    @staticmethod
    def get_pos_distance(pos1, pos2):
        return np.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1])
