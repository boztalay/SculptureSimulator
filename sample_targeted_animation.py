import math
import time
import random

import sculpy

class SampleTargetedAnimation(sculpy.TargetedAnimation):

    def __init__(self, row_count, column_count):
        super().__init__(row_count, column_count)

        self.patterns = []

        offset = -20000.0
        distance = 2000.0
        top = offset
        bottom = top - distance

        # Alternating rows 1
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if row % 2 == 0:
                    pattern_row.append(top) 
                else:
                    pattern_row.append(bottom) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

        # Alternating rows 2
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if row % 2 == 0:
                    pattern_row.append(bottom) 
                else:
                    pattern_row.append(top) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

        # Checkerboard 1
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if row % 2 == 0:
                    if column % 2 == 0:
                        pattern_row.append(top) 
                    else:
                        pattern_row.append(bottom) 
                else:
                    if column % 2 == 0:
                        pattern_row.append(bottom) 
                    else:
                        pattern_row.append(top) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

        # Checkerboard 2
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if row % 2 == 0:
                    if column % 2 == 0:
                        pattern_row.append(bottom) 
                    else:
                        pattern_row.append(top) 
                else:
                    if column % 2 == 0:
                        pattern_row.append(top) 
                    else:
                        pattern_row.append(bottom) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

        # Alternating columns 1
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if column % 2 == 0:
                    pattern_row.append(top) 
                else:
                    pattern_row.append(bottom) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

        # Alternating columns 2
        pattern = []
        for row in range(0, row_count):
            pattern_row = []
            for column in range(0, column_count):
                if column % 2 == 0:
                    pattern_row.append(bottom) 
                else:
                    pattern_row.append(top) 
            pattern.append(pattern_row)
        self.patterns.append(pattern)

    def get_next_targets(self, timestamp, time_delta, current_targets):
        # Index will increment every 3 seconds and wrap through the range [0, len(self.patterns)]
        index = int(timestamp / 3.0) % len(self.patterns)
        pattern = self.patterns[index]
        return pattern

ANIMATION_CLASS = SampleTargetedAnimation
