SculptureSimulator
==================

<p align="center">
  <img src="https://github.com/boztalay/SculptureSimulator/assets/1679999/b0d48cf5-c930-4d06-b07f-44beba6d31a0"/>
</p>

This is a lightweight simulator for the kinetic sculpture to help with
developing animations. Any animations you create with this can be used
directly on the physical sculpture!

### Prerequisites

You'll need Python 3 and VPython:
```
$ pip3 install vpython
```

### Getting Started

To run an animation, run the `sculpy.py` script with the name of your animation
module (which is just the file name without the `.py` extension):

```
$ python3 sculpy.py sample_animation
```

The simulator will open a browser window to render everything, and it'll run the
animation in there!

Press Crtl-C at any time to close the browser window and stop the script.

### Writing Animations

All animations are written as a subclass of `sculpy.Animation`. Every frame,
`sculpy` will ask your animation for what position each ball should be at for
the next frame.

There are three animation classes that you can subclass, each providing
slightly different APIs to use depending on your needs: `Animation`,
`ShaderStyleAnimation`, and `TargetedAnimation`.

#### `Animation` Subclasses

This is the base animation class, which asks your animation for whole frames of
positions. A simple `Animation` subclass can be found in `sample_animation.py`,
and a minimal version looks like this:

```python
import sculpy

class SampleAnimation(sculpy.Animation):

    # `timestamp`: the current animation time in seconds, starting at 0.0 for each animation
    # `time_delta`: the number of seconds since the last frame
    # `last_frame`: a 2D list of the positions of the last frame (as a list of rows)
    def get_next_frame(self, timestamp, time_delta, last_frame):
        return last_frame

ANIMATION_CLASS = SampleAnimation
```

#### `ShaderStyleAnimation` Subclasses

Shader-style animations are asked for ball positions one at a time, based on
their row and column numbers. This can be nice if your animation can be expressed
more mathematically, similar to a graphics shader if you're familiar with those.

A `ShaderStyleAnimation` subclass can be found in `rain_animation.py`, and a
minimal version looks like this:

```python
import sculpy

class SampleShaderStyleAnimation(sculpy.ShaderStyleAnimation):

    # `row`: the row number of the ball
    # `column`: the column number of the ball
    # `timestamp`: the current animation time in seconds, starting at 0.0 for each animation
    # `time_delta`: the number of seconds since the last frame
    # `last_position`: the position of the ball in the last frame
    def get_ball_position(self, row, column, timestamp, time_delta, last_position):
        return last_position

ANIMATION_CLASS = SampleShaderStyleAnimation
```

#### `TargetedAnimation` Subclasses

Lastly, the `TargetedAnimation` class helps abstract away the logic needed to
move balls smoothly between positions by asking for target positions, then
animating the balls to those targets for you. This is helpful for a style of
animation that hits a shape, holds it, then moves to the next shape.

A `TargetedAnimation` subclass can be found in `sample_targeted_animation.py`,
and a minimal version looks like this:

```python
import sculpy

class SampleTargetedAnimation(sculpy.TargetedAnimation):

    # `timestamp`: the current animation time in seconds, starting at 0.0 for each animation
    # `time_delta`: the number of seconds since the last frame
    # `current_targets`: a 2D list of the current targets for each ball (as a list of rows)
    def get_next_targets(self, timestamp, time_delta, current_targets):
       return current_targets

ANIMATION_CLASS = SampleTargetedAnimation
```

#### Notes, tips, etc

  - Valid position values range between 0.0 (at the top of the sculpture) and
    -95000.0 (all the way at the bottom of the sculpture's range)
  - There's a maximum velocity that the sculpture can move the balls, which is
    4500.0 points/s, or ~2.8 inches/s
    - The simulator doesn't enforce this limit, but it will issue warnings!
  - The sculpture runs at about 20 frames per second
  - Try to use `timestamp` and `time_delta` directly as much as you can (instead
    of e.g., hard-coding increments each frame, or assuming a fixed 50ms per frame)
