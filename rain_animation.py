import math
import time
import random

import sculpy

class RainAnimation(sculpy.ShaderAnimation):

    def __init__(self, row_count, column_count):
        super().__init__(row_count, column_count)

        self.ball_states = []
        for _ in range(0, row_count):
            ball_states_row = []
            for _ in range(0, column_count):
                ball_states_row.append(None)
            self.ball_states.append(ball_states_row)

    def get_ball_position(self, row, column, timestamp, time_delta, last_position):
        top = 0.0
        bottom = -90000.0
        base_velocity = 1500.0

        if timestamp == 0.0:
            return top

        ball_state = self.ball_states[row][column]
        velocity = base_velocity + (375.0 * (self.column_count - column - 1))

        new_position = last_position

        if ball_state is None:
            if random.randrange(0, 400) == 0:
                ball_state = False
        elif ball_state == False:
            new_position -= velocity * time_delta
            if new_position <= bottom:
                new_position = bottom
                ball_state = True
        elif ball_state == True:
            new_position += velocity * time_delta
            if new_position >= top:
                new_position = top
                ball_state = None

        self.ball_states[row][column] = ball_state
        return new_position

ANIMATION_CLASS = RainAnimation
