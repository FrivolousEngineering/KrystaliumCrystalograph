from typing import Tuple

import numpy as np

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
    def __init__(self, base_color: "str", radius: int, thickness: int, center: Point, begin_angle: int, end_angle: int, line_type: str):
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

    def setup(self):
        pass

    def setColorController(self, color_controler):
        self._color_controller = color_controler

    def draw(self, image, override_color: None = None, alpha = 1.0, thickness_modifier: float = 1, noise_modifier: float = 1.0):
        thickness_to_use = thickness_modifier * self._thickness

        pts = self.generateCirclePolyLines(self._center, self._radius, self._begin_angle, self._end_angle, noise=noise_modifier*self._noisegit )
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

    def generateCirclePolyLines(self, center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, *,
                                noise: float = 0.1):
        circle_length = (2 * math.pi * radius) * ((end_angle - begin_angle) / 360)
        num_segments = int(circle_length * NUM_SEGMENTS_PER_LENGTH)

        begin_angle_rad = math.radians(begin_angle + 180)
        end_angle_rad = math.radians(end_angle + 180)
        total_angle = end_angle_rad - begin_angle_rad

        spacing_between_angle = total_angle / (num_segments - 1)
        pts = []

        for segment in range(num_segments):
            # Calculate where the circle should be.
            circle = (-math.sin(segment * spacing_between_angle + begin_angle_rad) * radius,
                      math.cos(segment * spacing_between_angle + begin_angle_rad) * radius)
            pts.append(circle)

        pts = np.array(pts, np.int32)
        if noise != 0:
            noise_multiplier = self.generateNoiseMultiplierForCircle(num_segments, noise,
                                                                     int(num_segments / 8))
            pts = numpy.multiply(pts, noise_multiplier)

        # Now ensure that the centre of our curve is set correctly!
        centers = [center] * num_segments
        pts = numpy.add(centers, pts)

        # Force the results to be int, else we can't draw em
        pts = np.array(pts, np.int32)
        return pts

    @staticmethod
    def generateNoiseMultiplierForCircle(num_segments: int, noise: float,
                                         num_cap_segments_limit_noise: int = 0) -> np.array:
        """

        :param num_segments:
        :param noise:
        :param smooth_noise:
        :param num_cap_segments_limit_noise: On how many of the segments on the begin/end should the noise be limited
        :return:
        """
        noise_multiplier = []
        for segment in range(num_segments):
            # Calculate the noise
            rand_value = random.random()
            rand = math.sin(segment / 0.7) * rand_value + math.sin(segment / 1.1) * rand_value + math.sin(
                segment / 1.5) * rand_value

            noise_multiplier.append(0.5 * rand * noise + 0.5 * noise * random.random())

        noise_multiplier = savgol_filter(noise_multiplier, 5, 1)

        # Apply a linear scale to the begin & end segments
        if num_cap_segments_limit_noise > 0:
            cap_limit_per_step = 1 / num_cap_segments_limit_noise
            for limit_segment in range(num_cap_segments_limit_noise):
                noise_multiplier[limit_segment] *= limit_segment * cap_limit_per_step

                noise_multiplier[-(limit_segment + 1)] *= limit_segment * cap_limit_per_step

        for segment in range(num_segments):
            noise_multiplier[segment] += 1

        # Since want to offset the signal from the center, we need to rescale the 1d vector to 2d (so copy the column
        # to a second column)
        noise_multiplier = np.repeat(noise_multiplier[:, np.newaxis], 2, 1)

        return noise_multiplier
