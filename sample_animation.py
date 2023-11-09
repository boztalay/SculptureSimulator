import sculpy

class SampleAnimation(sculpy.Animation):

    def get_next_frame(self, timestamp, time_delta, last_frame):
        top = -30000.0
        bottom = -50000.0
        period = 20.0
        time_offset_per_row = period / float(self.row_count) / 2.0

        frame = last_frame

        for row in range(0, self.row_count):
            for column in range(0, self.column_count):
                row_time_offset = time_offset_per_row * float(row)
                row_time = timestamp + row_time_offset
                frame[row][column] = self.triangle(top, bottom, period, row_time)

        return frame

    def triangle(self, top, bottom, period, t):
        progress = (t / period) - int(t / period)

        if progress < 0.5:
            return sculpy.map_range(0.0, 0.5, top, bottom, progress)
        else:
            return sculpy.map_range(0.5, 1.0, bottom, top, progress)

ANIMATION_CLASS = SampleAnimation
