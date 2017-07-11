# Pygame Soccer

A variant of the game described in the paper [He, He, et al. "Opponent modeling in deep reinforcement learning." International Conference on Machine Learning. 2016][paper]. Pygame is used as the rendering framework. PyTMX is used to read the map file.

![screenshot](docs/screenshot.png "Screenshot")

Customized Minecraft texture is used for displaying the tiles. Reinforcement learning agent controls the player 1 (shown as the player Steve head), the computer agent controls the player 2 (shown as the creeper head). The agent who has the ball is bordered by a blue square (in this case, the creeper has the ball shown in the image). The goal field height has been extended to 4. See the [paper][paper] for the game rules.

## Installation

### Requirements

- [Python 3.6](https://www.continuum.io/)

Run the following to install all the dependencies locally.

```shell
pip install -e .
```

## Running

To test the reinforcement learning environment with the random agent, run `examples/test_env.py`.

To test the renderer, run `examples/test_renderer.py`. Press the arrow keys to control the player 1. Press key `1` to make the player 1 has ball; Press key `2` to take the ball away from the player 1.

## Development

### Software

- [Visual Studio Code](https://code.visualstudio.com/) for editing the text files.
- [Python extension for VSCode](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python) for linting Python files.
- [Tiled Map Editor](http://www.mapeditor.org/) for editing `.tmx` and `.tsx` files.
- [GIMP](https://www.gimp.org/) for editing the image files.

## Environment

### Controlling

The example code can be found in `examples/test_env.py`. The procedure to control the environment is as follows.

1. Create an enrionment. An optional argument `renderer_options` can be used to control the renderer behaviors. The definition of renderer options can be found in `soccer/renderer_options.py:RendererOptions`.
```python
soccer_env = soccer.SoccerEnvironment()
```
2. Reset the environment and get the initial observation. The observation is class containing the old state, the taken action, reward, and the next state. The definition can be found in `soccer/soccer_environment.py:SoccerObservation`.
```python
observation = soccer_env.reset()
```
3. Render the environment. The renderer will lazy load on the first call. Skip the call if you don't need the rendering.
```python
soccer_env.render()
```
4. Get the screenshot. The returned `screenshot` is a `numpy.ndarray`, the format is the same as the returned value of `scipy.misc.imread`. The previous step is required for this call to work.
```
screenshot = soccer_env.renderer.get_screenshot()
```
5. Take an action and get the observation. The action list is defined in `soccer/soccer_environment.py:SoccerEnvironment`.
```python
observation = soccer_env.take_action(action)
```
6. Check whether the state is terminal. See the [State](#state) section for details.
```python
if soccer_env.state.is_terminal():
  # Do something
```

### State

The state represents the internal state of the environment. The definition can be found in `soccer/soccer_environment.py:SoccerState`.

The state contains several things that can be controlled.

* Reset the state. The player positions, ball possession, and computer agent mode will be randomized. The time step will be set to 0.
```python
state.reset()
```
* Whether the state is terminal.
```python
is_terminal = state.is_terminal()
```
* Whether the player has won. The `player_index` is either 0 (Player) or 1 (Computer).
```python
has_won = state.is_player_win(player_index)
```
* Get or set the player position.
```python
pos = state.get_player_pos(player_index)
state.set_player_pos(player_index, pos)
```
* Get or set the possession of the ball.
```python
has_ball = state.get_player_ball(player_index)
state.set_player_ball(player_index, has_ball)
```
* Set the computer agent mode. The `mode` is either `DEFENSIVE` (Defensive) or `OFFENSIVE` (Offensive).
```python
state.set_computer_agent_mode(mode)
```

### Computer Agent Algorithm

The computer agent has 4 strategies according to the scenarios described in the [paper][paper]. The internal algorithm of either approaching or avoiding is by randomly moving the direction in either axis so that the Euclidean distance from the target is shorter or further.

* "Avoid opponent": See where the player is, avoid him.
* "Advance to goal": See where the leftmost goal is, select a random grid, approach it.
* "Defend goal": See where the rightmost goal is, select a random grid, approach it.
* "Intercept goal": See where the player is, approach him.

The two agents move in random order, i.e., every time the player plans to moves, the computer agent either moves first or follows the move by the player.

[paper]: https://www.umiacs.umd.edu/~hal/docs/daume16opponent.pdf