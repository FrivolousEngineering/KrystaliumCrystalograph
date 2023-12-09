from typing import Tuple

import numpy
import numpy as np
import cv2
import math
from scipy.signal import savgol_filter
import random
# Typing helpers
Image = np.ndarray
Point = Tuple[int, int]
Color = Tuple[int, int, int]


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

NUM_SEGMENTS_PER_LENGTH = 0.5


def createEmptyImage(size: Tuple[int, int]) -> Image:
    return np.zeros((*size[::-1], 3), dtype=np.uint8)


def drawTargetLines(image: Image) -> Image:
    """
    Draw the horizontal & vertical target line
    :param image:
    :return:
    """

    # Numpy uses the convention `rows, columns`, instead of `x, y`.
    # Therefore height, has to be before width.
    height, width = image.shape[:2]

    line_color = WHITE
    image = cv2.line(image, (int(width / 2), 0), (int(width / 2), height), line_color, 1)
    image = cv2.line(image, (0, int(height / 2)), (width, int(height / 2)), line_color, 1)
    return image


def generateCirclePolyLines(center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, *, noise: float = 0.1, smooth_noise: bool = True):
    circle_length = (2 * math.pi * radius) * ((end_angle - begin_angle) / 360)
    num_segments = int(circle_length * NUM_SEGMENTS_PER_LENGTH)


    begin_angle_rad = math.radians(begin_angle + 180)
    end_angle_rad = math.radians(end_angle + 180)
    total_angle = end_angle_rad - begin_angle_rad

    spacing_between_angle = total_angle / (num_segments - 1)
    pts = []

    for segment in range(num_segments):
        # Calculate where the circle should be.
        circle = (-math.sin(segment * spacing_between_angle + begin_angle_rad) * radius, math.cos(segment * spacing_between_angle + begin_angle_rad) * radius)
        pts.append(circle)

    pts = np.array(pts, np.int32)
    noise_multiplier = generateNoiseMultiplierForCircle(num_segments, noise, smooth_noise, int(num_segments / 8))
    pts = numpy.multiply(pts, noise_multiplier)

    # Now ensure that the centre of our curve is set correctly!
    centers = [center] * num_segments
    pts = numpy.add(centers, pts)

    # Force the results to be int, else we can't draw em
    pts = np.array(pts, np.int32)
    return pts


def generateNoiseMultiplierForCircle(num_segments: int, noise: float, smooth_noise: bool, num_cap_segments_limit_noise: int = 0) -> np.array:
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
        rand_value = np.random.random()
        rand = np.sin(segment / 0.7) * rand_value + np.sin(segment / 1.1) * rand_value + np.sin(
            segment / 1.5) * rand_value

        noise_multiplier.append(0.5 * rand * noise + 0.5 * noise * np.random.random())

    if smooth_noise:
        noise_multiplier = savgol_filter(noise_multiplier, 5, 1)
    else:
        noise_multiplier = np.array(noise_multiplier)

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


def drawCircleWithPolyLines(image: Image, color: Color, center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, line_thickness: int = 2, *, noise: float = 0.1, smooth_noise: bool = True, is_closed: bool = False) -> Image:
    pts = generateCirclePolyLines(center, radius, begin_angle, end_angle, noise=noise, smooth_noise=smooth_noise)
    pts = pts.reshape((-1, 1, 2))

    # Actually draw them
    image = cv2.polylines(image, [pts], is_closed, color, line_thickness)
    return image


def applyBlooming(image: np.ndarray, gausian_ksize: int = 9, blur_ksize: int = 5) -> np.ndarray:
    # Provide some blurring to image, to create some bloom.
    if gausian_ksize > 0:
        cv2.GaussianBlur(image, (gausian_ksize, gausian_ksize), 0, dst=image)
    if blur_ksize > 0:
        cv2.blur(image, ksize=(blur_ksize, blur_ksize), dst=image)
    return image


# Debug function for convenience
def drawLines(image, line_thickness = 2, override_color = None):
    height, width = image.shape[:2]
    center = (int(width / 2), int(height / 2))

    if override_color:
        image = drawCircleWithPolyLines(image, override_color, center, 100, 270, 360, line_thickness=line_thickness)
    else:
        image = drawCircleWithPolyLines(image, RED, center, 100, 270, 360, line_thickness=line_thickness)

    if not override_color:
        override_color = BLUE

    image = drawCircleWithPolyLines(image, override_color, center, 100, 0, 90,
                                    line_thickness=line_thickness)
    image = drawCircleWithPolyLines(image, override_color, center, radius=150, begin_angle=30,
                                    end_angle=45,
                                    line_thickness=line_thickness)
    image = drawCircleWithPolyLines(image, override_color, center, 150, 60, 75,
                                    line_thickness=line_thickness)

    return image


def drawCircles(image, line_thickness = 2, override_color = None):
    height, width = image.shape[:2]
    center = (int(width / 2), int(height / 2))
    small_cirlce_radius = 50
    large_circle_radius = 100

    normalized_small_circle_radius = 0.05 * (100/small_cirlce_radius)
    normalized_large_circle_radius = 0.05 * (100 / large_circle_radius)

    if not override_color:
        override_color = GREEN

    image = drawCircleWithPolyLines(image, override_color, tuple(numpy.add(center, (large_circle_radius, large_circle_radius))),
                                    large_circle_radius, 0, 360, is_closed=True, noise=normalized_large_circle_radius,
                                    line_thickness=line_thickness)
    image = drawCircleWithPolyLines(image, override_color,
                                    tuple(numpy.add(center, (small_cirlce_radius + 14, small_cirlce_radius + 14))),
                                    small_cirlce_radius, 0, 360, is_closed=True, noise=normalized_small_circle_radius,
                                    line_thickness=line_thickness)

    return image


def drawDoubleCircle(image, thickness = 6, radius = 150, start_angle = 185, end_angle = 265):
    height, width = image.shape[:2]
    center = (int(width / 2), int(height / 2))
    # As the noise is based on the radius, we want to normalize it in this case
    normalized_noise = 0.08 * (100/radius)

    pts_top = generateCirclePolyLines(center, int(radius - thickness / 2), start_angle, end_angle, noise=normalized_noise,
                                  smooth_noise=True)

    pts_bottom = generateCirclePolyLines(center, int(radius + thickness / 2), start_angle, end_angle, noise=normalized_noise,
                                  smooth_noise=True)


    # Due to winding order, we need to flip the bottom points again
    pts_bottom = numpy.flipud(pts_bottom)
    pts = numpy.append(pts_top, pts_bottom)

    pts = pts.reshape((-1, 1, 2))
    # Actually draw them
    image = cv2.fillPoly(image, [pts], YELLOW)

    return image


def draw(image, line_thickness = 2, override_color = None):
    image = drawLines(image, line_thickness, override_color = override_color)
    image = drawCircles(image, line_thickness=line_thickness, override_color=override_color)
    image = drawDoubleCircle(image, thickness=1, radius=150, start_angle=185, end_angle=209)

    image = drawDoubleCircle(image, thickness=3, radius=150, start_angle=213, end_angle=237)
    image = drawDoubleCircle(image, thickness=6, radius=150, start_angle=241, end_angle=265)

    image = drawDoubleCircle(image, thickness=1, radius=130, start_angle=197, end_angle=221)
    return image


def applyFlickerToColors():
    global RED, YELLOW, GREEN, BLUE
    red_hsv = cv2.cvtColor(np.uint8([[RED]]), cv2.COLOR_RGB2HSV)

    rand = np.random.random()
    rand -= 0.4
    rand *= 50

    red_hsv[0][0][2] = min(max(red_hsv[0][0][2] + rand, 0), 255)
    red_rgb = cv2.cvtColor(red_hsv, cv2.COLOR_HSV2RGB)
    RED = (int(red_rgb[0][0][0] + 0.5), int(red_rgb[0][0][1] + 0.5), int(red_rgb[0][0][2]+0.5))

    yellow_hsv = cv2.cvtColor(np.uint8([[YELLOW]]), cv2.COLOR_RGB2HSV)
    rand = np.random.random()
    rand -= 0.4
    rand *= 50
    yellow_hsv[0][0][2] = min(max(yellow_hsv[0][0][2] + rand, 0), 255)
    yellow_rgb = cv2.cvtColor(yellow_hsv, cv2.COLOR_HSV2RGB)
    YELLOW = (int(yellow_rgb[0][0][0] + 0.5), int(yellow_rgb[0][0][1] + 0.5), int(yellow_rgb[0][0][2] + 0.5))

    green_hsv = cv2.cvtColor(np.uint8([[GREEN]]), cv2.COLOR_RGB2HSV)
    rand = np.random.random()
    rand -= 0.4
    rand *= 50
    green_hsv[0][0][2] = min(max(green_hsv[0][0][2] + rand, 0), 255)
    green_rgb = cv2.cvtColor(green_hsv, cv2.COLOR_HSV2RGB)
    GREEN = (int(green_rgb[0][0][0] + 0.5), int(green_rgb[0][0][1] + 0.5), int(green_rgb[0][0][2] + 0.5))

    blue_hsv = cv2.cvtColor(np.uint8([[BLUE]]), cv2.COLOR_RGB2HSV)
    rand = np.random.random()
    rand -= 0.4
    rand *= 50
    blue_hsv[0][0][2] = min(max(blue_hsv[0][0][2] + rand, 0), 255)
    blue_rgb = cv2.cvtColor(blue_hsv, cv2.COLOR_HSV2RGB)
    BLUE = (int(blue_rgb[0][0][0] + 0.5), int(blue_rgb[0][0][1] + 0.5), int(blue_rgb[0][0][2] + 0.5))
    pass


def drawVisualTest(image):

    # I know it's hella hacky. But suuuusssssh
    applyFlickerToColors()

    draw(image, line_thickness=4)
    applyBlooming(image, gausian_ksize=25, blur_ksize=25)
    applyBlooming(image)
    draw(image)
    applyBlooming(image)
    #draw(image, override_color=WHITE, line_thickness=1)
    #applyBlooming(image)
    draw(image, line_thickness=2)
    applyBlooming(image, gausian_ksize=3, blur_ksize=3)
    #draw(image, line_thickness=1, override_color=WHITE)
    #applyBlooming(image, gausian_ksize=3, blur_ksize=0)
    image = drawTargetLines(image)
    return image


if __name__ == '__main__':
    img = createEmptyImage((1024, 768))
    height, width = img.shape[:2]
    center = (int(width / 2), int(height / 2))

    drawVisualTest(img)
    cv2.imshow('Test', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey()

