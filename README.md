# Pygame Soccer

A Pygame soccer environment.

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

The example code can be found in `examples/test_env.py`. The procedure to control the environment is as follows.

1. Create an enrionment. An optional argument `renderer_max_fps` is given to restrain the max frames per second of the rendering.
```python
soccer_env = soccer.SoccerEnvironment(renderer_max_fps=10)
```
2. Reset the environment and get the initial observation. The observation is class containing the old state, the taken action, reward, and the next state. The definition can be found in `soccer/soccer_environment.py:SoccerObservation`.
```python
observation = soccer_env.reset()
```
3. Render the environment. The renderer will lazy load on the first call. Skip the call if you don't need the rendering to speed up the running.
```python
soccer_env.render()
```
4. Take an action and get the observation. The action list is defined in `soccer/soccer_environment.py:SoccerEnvironment`.
```python
observation = soccer_env.take_action(action)
```
5. Check whether the state is terminal. The state is the internal state of the environment and defined in `soccer/soccer_environment.py:SoccerState`.
```python
if soccer_env.state.is_terminal():
  # Do something
```
