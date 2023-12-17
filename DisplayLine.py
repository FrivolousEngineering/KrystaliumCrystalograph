from functools import cache
from typing import Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

from FlickeringColor import FlickeringColor
from typing import Tuple, Optional, Dict
import random
import numpy
import numpy as np
import cv2
import math
from scipy.signal import savgol_filter

NUM_SEGMENTS_PER_LENGTH = 0.5
Image = np.ndarray
Point = Tuple[int, int]
Color = Tuple[int, int, int]


class DisplayLine:
    def __init__(self, base_color: "str", radius: int, thickness: int, center: Point, begin_angle: int, end_angle: int, line_type: str, spikes):
        self._color_name = base_color
        self._radius: radius = radius
        self._thickness: int = thickness
        self._center: Point = center
        self._begin_angle: int = begin_angle
        self._end_angle: int = end_angle
        self.line_type = line_type
        self._noise = 0.08 * (100 / radius)  # normalize the noise
        self._is_closed = False
        self._color_controller = None
        if spikes is None:
            spikes = []
        self._spikes = spikes

        self._max_variation = 25
        self._variation_number = random.randint(0, self._max_variation)

    def setup(self):
        pass

    def setColorController(self, color_controler):
        self._color_controller = color_controler

    def draw(self, image, override_color: None = None, alpha = 1.0, thickness_modifier: float = 1, noise_modifier: float = 1.0):
        thickness_to_use = thickness_modifier * self._thickness

        pts = self.generateCirclePolyLines(self._center, self._radius, self._begin_angle, self._end_angle, noise=noise_modifier*self._noise )
        pts = pts.reshape((-1, 1, 2))

        color_to_use = self._color_controller.getColor(self._color_name)
        if override_color is not None:
            color_to_use = self._color_controller.getColor(override_color)

        if alpha < 1.0:
            overlay = image.copy()
            cv2.polylines(overlay, [pts], self._is_closed, color_to_use, int(thickness_to_use))

            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        else:
            # Actually draw them
            image = cv2.polylines(image, [pts], self._is_closed, color_to_use, int(thickness_to_use))
        return image

    def generateModifiedRadius(self, num_segments):
        pts = np.empty(num_segments)
        pts.fill(self._radius)

        # Calculate on what segment the spike needs to be!
        total_angle_range = abs(self._begin_angle - self._end_angle)
        angle_per_segment = num_segments / total_angle_range

        for spike_angle, spike_width, intensity in self._spikes:
            angle_difference = abs(self._begin_angle - spike_angle)
            segments_difference = angle_difference * angle_per_segment
            segments_width = int(spike_width * angle_per_segment)

            segments = np.arange(segments_width)
            segments = numpy.append(segments, numpy.flipud(segments))
            segments = (segments / (segments_width - 1)) * intensity + 1
            window = pts[int(segments_difference-segments_width):int(segments_difference+segments_width)]
            window = numpy.multiply(window, segments)
            pts[int(segments_difference - segments_width):int(segments_difference + segments_width)] = window
            #pts[int(segments_difference-segments_width):int(segments_difference+segments_width)] ==   extra_data

        kern_size = 11
        cutoff_size = int((kern_size - 1) / 2)

        pts = self.smooth(pts, kern_size)
        pts = self.smooth(pts[cutoff_size:-cutoff_size], kern_size)
        return pts[cutoff_size:-cutoff_size]

    @staticmethod
    def smooth(x, window_len=11, window='blackman'):
        """smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
            x: the input signal
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal

        example:

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)

        see also:

        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter

        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        """

        if x.ndim != 1:
            raise ValueError

        if x.size < window_len:
            raise ValueError

        if window_len < 3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError

        s = numpy.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
        if window == 'flat':  # moving average
            w = numpy.ones(window_len, 'd')
        else:
            w = eval('numpy.' + window + '(window_len)')

        y = numpy.convolve(w / w.sum(), s, mode='valid')
        return y

    def generateCirclePolyLines(self, center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, *,
                                noise: float = 0.1):
        circle_length = (2 * np.pi * radius) * ((end_angle - begin_angle) / 360)
        num_segments = int(circle_length * NUM_SEGMENTS_PER_LENGTH)

        begin_angle_rad = np.radians(begin_angle + 180)
        end_angle_rad = np.radians(end_angle + 180)
        total_angle = end_angle_rad - begin_angle_rad

        spacing_between_angle = total_angle / (num_segments - 1)

        modified_radius = self.generateModifiedRadius(num_segments)

        # Calculate where the circle should be using NumPy array operations.
        segments = np.arange(num_segments)
        circle_x = -np.sin(segments * spacing_between_angle + begin_angle_rad) * modified_radius
        circle_y = np.cos(segments * spacing_between_angle + begin_angle_rad) * modified_radius

        # Combine x and y coordinates into a single NumPy array.
        pts = np.column_stack((circle_x, circle_y))
        pts = np.array(pts, np.int32)

        #pts = numpy.multiply(pts, spike_modifier)

        if noise != 0:
            noise_multiplier = self.generateNoiseMultiplierForCircle(num_segments, noise,
                                                                     min(int(num_segments / 8), 5), self._variation_number)
            if self._variation_number > self._max_variation:
                self._variation_number = 0
            else:
                self._variation_number += 1
            pts = numpy.multiply(pts, noise_multiplier)

        # Now ensure that the centre of our curve is set correctly!
        centers = [center] * num_segments
        pts = numpy.add(centers, pts)

        # Force the results to be int, else we can't draw em
        pts = np.array(pts, np.int32)
        return pts

    @staticmethod
    @cache
    def generateNoiseMultiplierForCircle(num_segments: int, noise: float,
                                         num_cap_segments_limit_noise: int, variation: int) -> np.array:
        # Generate random values for all segments at once
        rand_values = np.random.random(num_segments)

        # Calculate the noise using vectorized operations
        segments = np.arange(num_segments)
        rand = np.sin(segments / 0.7) * rand_values + np.sin(segments / 1.1) * rand_values + np.sin(
            segments / 1.5) * rand_values
        noise_multiplier = 0.5 * rand * noise + 0.5 * noise * np.random.random(num_segments)

        # Apply Savitzky-Golay filter for smoothing
        noise_multiplier = savgol_filter(noise_multiplier, 5, 1)

        # Apply a linear scale to the begin & end segments using vectorized operations
        if num_cap_segments_limit_noise > 0:
            cap_limit_per_step = 1 / num_cap_segments_limit_noise
            limit_segments = np.arange(num_cap_segments_limit_noise)
            noise_multiplier[:num_cap_segments_limit_noise] *= limit_segments * cap_limit_per_step
            # Flip the points as we're working from different direction here
            noise_multiplier[-num_cap_segments_limit_noise:] *= numpy.flipud(limit_segments) * cap_limit_per_step

        # Add 1 to all segments using vectorized operations
        noise_multiplier += 1

        # Reshape the 1D vector to a 2D array with two columns
        noise_multiplier = np.repeat(noise_multiplier[:, np.newaxis], 2, axis=1)

        return noise_multiplier
