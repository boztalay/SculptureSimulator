import enum
import importlib
import math
import sys
import time

from vpython import *

FRAME_RATE = 20

ROW_COUNT = 10
COLUMN_COUNT = 8

MAX_DISTANCE_STEPS = 95000.0
MAX_BALL_VELOCITY = 4500.0
STEP_SIZE_MM = (5.0 * 12.0 * 25.4) / MAX_DISTANCE_STEPS
BALL_RADIUS_MM = 1.0 * 25.4 / 2.0
BALL_DIAMETER_MM = BALL_RADIUS_MM * 2.0
BALL_SPACING_MM = 50.0

def map_range(in_min, in_max, out_min, out_max, value):
    if in_min == in_max:
        return out_max

    return (((value - in_min) / (in_max - in_min)) * (out_max - out_min)) + out_min

def clamp(min_value, max_value, value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def map_range_clamp(in_min, in_max, out_min, out_max, value):
    mapped_value = map_range(in_min, in_max, out_min, out_max, value)
    return clamp(out_min, out_max, mapped_value)

class Animation():

    def __init__(self, row_count, column_count):
        self.row_count = row_count
        self.column_count = column_count

    def get_next_frame(self, timestamp, time_delta, last_frame):
        raise NotImplementedError('Animation subclasses must implement get_next_frame()')

class ShaderStyleAnimation(Animation):

    def get_next_frame(self, timestamp, time_delta, last_frame):
        next_frame = []

        for row in range(0, self.row_count):
            next_row = []

            for column in range(0, self.column_count):
                last_position = last_frame[row][column]
                next_position = self.get_ball_position(row, column, timestamp, time_delta, last_position)
                next_row.append(next_position)

            next_frame.append(next_row)

        for row in next_frame:
            if None in row:
                return None

        return next_frame

    def get_ball_position(self, row, column, timestamp, time_delta, last_position):
        raise NotImplementedError('ShaderStyleAnimation subclasses must implement get_next_frame()')

class TargetedAnimation(Animation):

    def __init__(self, row_count, column_count):
        super().__init__(row_count, column_count)

        self.targets = []
        for _ in range(0, row_count):
            target_row = []
            for _ in range(0, column_count):
                target_row.append(0.0)
            self.targets.append(target_row)

        self.velocity = MAX_BALL_VELOCITY * 0.9

    def get_next_frame(self, timestamp, time_delta, last_frame):
        next_targets = self.get_next_targets(timestamp, time_delta, self.targets)
        if timestamp == 0.0:
            return next_targets

        self.targets = next_targets

        new_frame = []
        for row_index, row in enumerate(last_frame):
            new_row = []

            for column_index, position in enumerate(row):
                target = self.targets[row_index][column_index]

                distance_to_move = self.velocity * time_delta
                next_position = target

                delta = abs(target - position)
                if delta > distance_to_move:
                    if position > target:
                        next_position = position - distance_to_move
                    else:
                        next_position = position + distance_to_move

                new_row.append(next_position)
            new_frame.append(new_row)

        return new_frame

    def get_next_targets(self, timestamp, time_delta, current_targets):
        raise NotImplementedError('TargetedAnimation subclasses must implement get_next_targets()')

class SimulatedSculpture():

    def __init__(self, row_count, column_count):
        self.row_count = row_count
        self.column_count = column_count

        overall_width = BALL_SPACING_MM * row_count
        overall_depth = BALL_SPACING_MM * column_count
        overall_height = STEP_SIZE_MM * MAX_DISTANCE_STEPS

        self.resize_canvas(overall_width, overall_height)
        self.make_bounding_box(overall_width, overall_depth, overall_height)
        self.make_balls(overall_width, overall_depth, overall_height)

        self.last_frame_time = None

    def resize_canvas(self, overall_width, overall_height):
        current_canvas = canvas.get_selected()
        current_canvas.width = overall_width / 0.95
        current_canvas.height = overall_height / 1.55

    def make_bounding_box(self, overall_width, overall_depth, overall_height):
        margin = BALL_RADIUS_MM * 2.0
        box_width = overall_width + margin
        box_depth = overall_depth + margin
        box_height = overall_height + margin

        rightmost = box_width / 2.0
        leftmost = -1.0 * rightmost
        frontmost = box_depth / 2.0
        backmost = -1.0 * frontmost
        uppermost = box_height / 2.0
        lowermost = -1.0 * uppermost

        radius = 3.0

        # Top square
        curve(
            pos=[
                vector(rightmost, uppermost, frontmost),
                vector(leftmost,  uppermost, frontmost),
                vector(leftmost,  uppermost, backmost),
                vector(rightmost, uppermost, backmost),
                vector(rightmost, uppermost, frontmost)
            ],
            radius=radius
        )

        # Bottom square
        curve(
            pos=[
                vector(rightmost, lowermost, frontmost),
                vector(leftmost,  lowermost, frontmost),
                vector(leftmost,  lowermost, backmost),
                vector(rightmost, lowermost, backmost),
                vector(rightmost, lowermost, frontmost)
            ],
            radius=radius
        )

        # Sides
        curve(pos=[vector(rightmost, uppermost, frontmost), vector(rightmost, lowermost, frontmost)], radius=radius)
        curve(pos=[vector(rightmost, uppermost, backmost),  vector(rightmost, lowermost, backmost)],  radius=radius)
        curve(pos=[vector(leftmost,  uppermost, backmost),  vector(leftmost,  lowermost, backmost)],  radius=radius)
        curve(pos=[vector(leftmost,  uppermost, frontmost), vector(leftmost,  lowermost, frontmost)], radius=radius)

    def make_balls(self, overall_width, overall_depth, overall_height):
        ball_row_offset = (overall_width / 2.0) - BALL_DIAMETER_MM
        ball_column_offset = (overall_depth / 2.0) - BALL_DIAMETER_MM
        self.ball_start_y = overall_height / 2.0

        self.balls = []
        for row_index in range(0, self.row_count):
            ball_row = []
            for column_index in range(0, self.column_count):
                ball_x = ball_row_offset - (BALL_SPACING_MM * row_index)
                ball_z = ball_column_offset - (BALL_SPACING_MM * column_index)
                ball = sphere(pos=vector(ball_x, self.ball_start_y, ball_z), radius=BALL_RADIUS_MM, color=color.white)
                ball_row.append(ball)
            self.balls.append(ball_row)

    def get_ball_positions(self):
        frame = []
        for row_index, ball_row in enumerate(self.balls):
            frame_row = []
            for column_index, ball in enumerate(ball_row):
                position = int(round((ball.pos.y - self.ball_start_y) / STEP_SIZE_MM))
                frame_row.append(position)
            frame.append(frame_row)

        return frame

    def set_ball_positions(self, frame):
        last_positions = self.get_ball_positions()

        now = time.monotonic()
        time_since_last_frame = None

        if self.last_frame_time is not None:
            time_since_last_frame = now - self.last_frame_time
        self.last_frame_time = now

        for row_index, row in enumerate(frame):
            for column_index, frame_position in enumerate(row):
                if frame_position > 0.0:
                    print(f'WARNING: Ball was commanded to move above the top of the sculpture! {frame_position}')
                elif frame_position < -1.0 * MAX_DISTANCE_STEPS:
                    print(f'WARNING: Ball was commanded to move beyond the range of the sculpture! {frame_position} vs -{MAX_DISTANCE_STEPS}')

                last_position = last_positions[row_index][column_index]
                if time_since_last_frame is not None:
                    velocity = float(frame_position - last_position) / time_since_last_frame
                    if abs(velocity) > MAX_BALL_VELOCITY:
                        print(f'WARNING: Ball was commanded to move faster than the max velocity! ({abs(velocity)} vs {MAX_BALL_VELOCITY} points/s)')
                ball = self.balls[row_index][column_index]
                position = self.ball_start_y + (frame_position * STEP_SIZE_MM)
                ball.pos = vector(ball.pos.x, position, ball.pos.z)

class Animator():

    def __init__(self, sculpture, animation_name):
        self.sculpture = sculpture

        animation_module = importlib.import_module(animation_name)
        animation_class = animation_module.ANIMATION_CLASS
        self.animation = animation_class(self.sculpture.row_count, self.sculpture.column_count)

    def run_animation(self):
        last_frame_time = None

        initial_frame = self.animation.get_next_frame(0.0, 0.0, self.sculpture.get_ball_positions())
        self.sculpture.set_ball_positions(initial_frame)

        start_time = time.monotonic()

        while True:
            last_frame = self.sculpture.get_ball_positions()

            next_frame_time = time.monotonic() - start_time
            time_delta = 0.0
            if last_frame_time is not None:
                time_delta = next_frame_time - last_frame_time

            next_frame = self.animation.get_next_frame(next_frame_time, time_delta, last_frame)
            if next_frame is None:
                break

            self.sculpture.set_ball_positions(next_frame)
            last_frame_time = next_frame_time

            rate(FRAME_RATE)

def main(animation_name):
    sculpture = SimulatedSculpture(ROW_COUNT, COLUMN_COUNT)
    animator = Animator(sculpture, animation_name)
    animator.run_animation()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:')
        print('    python3 sculpy.py <ANIMATION_MODULE_NAME>')
        sys.exit(1)

    main(sys.argv[1])
