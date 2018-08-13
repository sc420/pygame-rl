# User-defined modules
import pygame_rl.util.file_util as file_util


class Options(object):
    """The options for the soccer environment.
    """
    # Resource names
    map_resource_name = 'pygame_rl/data/map/soccer/soccer.tmx'

    # Map path
    map_path = None

    # Team size
    team_size = 1

    # Frame skip for AI
    ai_frame_skip = 1

    def __init__(self, map_path=None, team_size=1, ai_frame_skip=1):
        # Save the map path or use the internal resource
        if map_path:
            self.map_path = map_path
        else:
            self.map_path = file_util.get_resource_path(self.map_resource_name)
        # Save the team size
        self.team_size = team_size
        # Save the frame skip
        self.ai_frame_skip = ai_frame_skip

    @property
    def agent_size(self):
        return 2 * self.team_size
