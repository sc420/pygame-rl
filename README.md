# Pygame Soccer

A variant of the game described in the paper [He, He, et al. "Opponent modeling in deep reinforcement learning." International Conference on Machine Learning. 2016][paper]. Pygame is used as the rendering framework. PyTMX is used to read the map file. Customized Minecraft texture is used for displaying the tiles.

![screenshot](docs/screenshot.png "Screenshot")

Reinforcement learning agent controls the agent 1 (shown as the player Steve head), the computer agent controls the agent 2 (shown as the pig head). The agent who has the ball is bordered by a blue square (in this case, the pig has the ball shown in the image).

When the player carries the ball to the rightmost goal field, a reward of 1.0 is given; When the computer carries the ball to the leftmost goal field, a reward of -1.0 is given. The episode ends when either one of the agent carries the ball to its goal field or the time step reaches 100. See the [paper][paper] for the game rules.

## Installation

## Requirements

- [Python 3.6](https://www.continuum.io/)

## Getting Started

1. Clone the repository.
2. Open a command line and change the working directory to the cloned directory.
3. Install the package in [editable](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) mode because this package is not intended to be published.
```shell
pip install -e .
```

## Running the Samples

To test the reinforcement learning environment with the random player agent, run `sample/environment.py`.

To test the renderer with 4 agents, run `sample/renderer.py`. Press the arrow keys to control the agent 1.

## Using

### Interacting with the Environment

The sample code can be found in `sample/environment.py`. The procedure to control the environment is as follows.

1. Create an environment options. An optional argument `team_size` of either 1 or 2 can be specified to set the team size. An optional argument `spawn_bounds` can be specified to set the spawn bounds. The definition can be found in `pygame_soccer/soccer/soccer_environment.py:SoccerEnvironmentOptions`.
```python
env_options = soccer_environment.SoccerEnvironmentOptions(team_size=1)
```
2. Create an environment with the options. An optional argument `renderer_options` can be used to control the renderer behaviors. The definition can be found in `pygame_soccer/soccer/soccer_renderer.py:RendererOptions`.
```python
soccer_env = soccer_environment.SoccerEnvironment(options=env_options)
```
3. Reset the environment and get the initial observation. The observation is a class containing the old state, the taken action, reward, and the next state. The definition can be found in `pygame_soccer/soccer/soccer_environment.py:SoccerObservation`.
```python
observation = soccer_env.reset()
```
4. Render the environment. The renderer will lazy load on the first call. Skip the call if you don't need the rendering.
```python
soccer_env.render()
```
5. Get the screenshot. The returned `screenshot` is a `numpy.ndarray`, the format is the same as the returned value of `scipy.misc.imread`. The previous step is required for this call to work.
```
screenshot = soccer_env.renderer.get_screenshot()
```
6. Take an action and get the observation. A list of actions can be used in `soccer_env.actions`. If the team size is bigger than 1, `action` should be a list of actions.
```python
action = soccer_env.actions[0]
observation = soccer_env.take_action(action)
```
7. Check whether the state is terminal. See the [Controlling the State](#controlling-the-state) section for details.
```python
if soccer_env.state.is_terminal():
  # Do something
```

### Controlling the State

The state represents the internal state of the environment. The definition can be found in `pygame_soccer/soccer/soccer_environment.py:SoccerState`.

The state contains several things that can be controlled. `agent_index` should be calculated by calling `soccer_env.get_agent_index(team_name, team_agent_index)`, where a list of team name in `soccer_env.team_names` can be used as `team_name` and `team_agent_index` should be smaller than `env_options.team_size`.

* Reset the state. The agent positions, ball possession and agent mode will be randomized. The last taken action will be cleared. The time step will be set to 0.
```python
state.reset()
```
* Whether the state is terminal.
```python
is_terminal = state.is_terminal()
```
* Whether one team has won. ``
```python
has_won = state.is_team_win(team_name)
```
* Get or set the agent position. `pos` is a list with 2 elements which represent x and y positions on the grid.
```python
pos = state.get_agent_pos(agent_index)
state.set_agent_pos(agent_index, pos)
```
* Get or set the possession of the ball.
```python
has_ball = state.get_agent_ball(agent_index)
state.set_agent_ball(agent_index, has_ball)
```
* Get or set the agent mode. `agent_index` should be the computer agent index, otherwise, `None` is returned in get method and it has no effect in set method.
```python
state.get_agent_mode(agent_index)
mode = soccer_env.modes[0]
state.set_agent_mode(agent_index, mode)
```
* Get the last taken action of the computer agent. The action is always a list. `agent_index` should be the computer agent index, otherwise, `None` is returned.
```python
action = state.get_agent_action(agent_index)
```

### Changing the Map

The map data is embedded in the map file `pygame_soccer/data/map/soccer.tmx`. Config file path is associated with layers regarding the name to positions mapping. See `pygame_soccer/renderer/pygame_renderer.py` for more information.

To modify the map, for example.

* Change the walkable field: Modify the layer `ground` in `pygame_soccer/data/map/soccer.tmx` as `pygame_soccer/data/map/ground_tile.yaml` is associated with the layer.
* Change the goal field: Modify the layer `goal` in `pygame_soccer/data/map/soccer.tmx` as `pygame_soccer/data/map/goal_tile.yaml` is associated with the layer.
* Change the moving agents: Modify the layer `agent` in `pygame_soccer/data/map/soccer.tmx` and the mapping file `pygame_soccer/data/map/agent_sprite.yaml`.

## Knowledge

### Computer Agent Algorithm

The computer agent has 4 strategies according to the scenarios described in the [paper][paper]. The internal algorithm of either approaching or avoiding is by randomly moving the direction in either axis so that the Euclidean distance from the target is shorter or further.

* "Avoid opponent": See where the nearest player is, avoid him.
* "Advance to goal": See where the leftmost goal field is, select a grid which has the maximum distance from the nearest player, approach it.
* "Defend goal": See where the rightmost goal field is, select a grid which has the minimum distance from the player who possesses the ball, approach it.
* "Intercept goal": See where the player who possesses the ball is, approach him.

The two agents move in random order, i.e., every time the player plans to moves, the computer agent either moves first or follows the move by the player.

## Development

### Software

* [Visual Studio Code](https://code.visualstudio.com/) for editing the text files.
* [Python extension for VSCode](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python) for linting Python files.
* [Tiled Map Editor](http://www.mapeditor.org/) for editing `.tmx` and `.tsx` files.
* [GIMP](https://www.gimp.org/) for editing the image files.

### Running the Tests

1. Install the test dependencies.
```shell
pip install .[test]
```
2. Run the tests with Pytest.
```shell
python tests/main.py
```

### Resources

The materials of the tileset comes from the following links:

* [Minecraft Sprite](http://minecraft.gamepedia.com/index.php?title=File:BlockCSS.png)
* [Minecraft Pig Face Sprite](https://kandipatterns.com/patterns/characters/minecraft-pig-face-16x16-21979)

[paper]: https://www.umiacs.umd.edu/~hal/docs/daume16opponent.pdf