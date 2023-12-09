from typing import Tuple

import numpy
import numpy as np
import cv2
import math
from scipy.signal import savgol_filter
import blooming
import random
# Typing helpers
Image = np.ndarray
Point = Tuple[int, int]
Color = Tuple[int, int, int]


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN= (0, 255, 0)


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


def drawHalfCircleNoRound(image):
    height, width = image.shape[0:2]
    # Ellipse parameters
    radius = 100
    center = (width / 2, height - 25)
    axes = (radius, radius)
    angle = 0
    start_angle = 180
    end_angle = 360
    # When thickness == -1 -> Fill shape
    thickness = -1

    # Draw black half circle
    cv2.ellipse(image, center, axes, angle, start_angle, end_angle, BLACK, thickness)

    axes = (radius - 10, radius - 10)
    # Draw a bit smaller white half circle
    cv2.ellipse(image, center, axes, angle, start_angle, end_angle, WHITE, thickness)


def drawHalfCircleRounded(image):
    height, width = image.shape[0:2]
    # Ellipse parameters
    radius = 100
    center = (width / 2, height - 25)
    axes = (radius, radius)
    angle = 0
    start_angle = 180
    end_angle = 360
    thickness = 10

    # http://docs.opencv.org/modules/core/doc/drawing_functions.html#ellipse
    cv2.ellipse(image, center, axes, angle, start_angle, end_angle, BLACK, thickness)


def generateCirclePolyLines(center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, *, segments: int = 10, noise: float = 0.1, smooth_noise: bool = True):
    assert segments >= 2, "We must have at least 2 segments"
    begin_angle_rad = math.radians(begin_angle + 180)
    end_angle_rad = math.radians(end_angle + 180)
    total_angle = end_angle_rad - begin_angle_rad

    spacing_between_angle = total_angle / (segments - 1)
    pts = []

    for segment in range(segments):
        # Calculate where the circle should be.
        circle = (-math.sin(segment * spacing_between_angle + begin_angle_rad) * radius, math.cos(segment * spacing_between_angle + begin_angle_rad) * radius)
        pts.append(circle)

    pts = np.array(pts, np.int32)

    noise_multiplier = generateNoiseMultiplierForCircle(segments, noise, smooth_noise)
    pts = numpy.multiply(pts, noise_multiplier)

    # Now ensure that the centre of our curve is set correctly!
    centers = [center] * segments
    pts = numpy.add(centers, pts)

    # Force the results to be int, else we can't draw em
    pts = np.array(pts, np.int32)
    return pts


def generateNoiseMultiplierForCircle(num_segments: int, noise: float, smooth_noise: bool) -> np.array:
    noise_multiplier = []
    for segment in range(num_segments):
        # Calculate the noise
        rand = np.sin(segment / 0.7) * np.random.random(1) + np.sin(segment / 1.1) * np.random.random(1) + np.sin(
            segment / 1.5) * np.random.random(1)
        noise_multiplier.append(1 + rand[0] * noise)

    if smooth_noise:
        noise_multiplier = savgol_filter(noise_multiplier, 5, 1)
    else:
        noise_multiplier = np.array(noise_multiplier)

    # Since want to offset the signal from the center, we need to rescale the 1d vector to 2d (so copy the column
    # to a second column)
    noise_multiplier = np.repeat(noise_multiplier[:, np.newaxis], 2, 1)

    return noise_multiplier


def drawCircleWithPolyLines(image: Image, color: Color, center: Point, radius: int, begin_angle: int = 0, end_angle: int = 90, line_thickness: int = 2, *, segments: int = 50, noise: float = 0.1, smooth_noise: bool = True, is_closed: bool = False) -> Image:
    pts = generateCirclePolyLines(center, radius, begin_angle, end_angle, segments =segments, noise=noise, smooth_noise=smooth_noise)

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


def drawLines(image, line_thickness = 2, override_color = None):
    # Debug function for convenience
    if override_color:
        image = drawCircleWithPolyLines(image, override_color, center, 100, 0, 90, segments=50, line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, override_color, center, radius=150, segments=15, begin_angle=30, end_angle=45,
                                        line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, override_color, center, 150, 60, 75, segments=10, line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, override_color, center, 100, 270, 360, segments=50, line_thickness=line_thickness)
    else:
        image = drawCircleWithPolyLines(image, BLUE, center, 100, 0, 90, segments=50, line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, BLUE, center, radius=150, segments=15, begin_angle=30, end_angle=45, line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, BLUE, center, 150, 60, 75, segments=10, line_thickness=line_thickness)
        image = drawCircleWithPolyLines(image, RED, center, 100, 270, 360, segments=50, line_thickness=line_thickness)
    return image


def drawCircles(image, line_thickness = 2, override_color = None):
    if override_color:
        cirlce_radius = 100
        image = drawCircleWithPolyLines(image, override_color, tuple(numpy.add(center, (cirlce_radius, cirlce_radius))),
                                        cirlce_radius, 0, 360, is_closed=True, segments=200, noise=0.05,
                                        line_thickness=line_thickness)
        cirlce_radius = 50
        image = drawCircleWithPolyLines(image, override_color,
                                        tuple(numpy.add(center, (cirlce_radius + 14, cirlce_radius + 14))),
                                        cirlce_radius, 0, 360, is_closed=True, segments=200, noise=0.05,
                                        line_thickness=line_thickness)
    else:
        cirlce_radius = 100
        image = drawCircleWithPolyLines(image, GREEN, tuple(numpy.add(center, (cirlce_radius, cirlce_radius))), cirlce_radius, 0, 360, is_closed=True, segments=200, noise=0.05, line_thickness=line_thickness)
        cirlce_radius = 50
        image = drawCircleWithPolyLines(image, GREEN, tuple(numpy.add(center, (cirlce_radius+14, cirlce_radius+14))),
                                        cirlce_radius, 0, 360, is_closed=True, segments=200, noise=0.05, line_thickness=line_thickness)
    return image


def draw(image, line_thickness = 2, override_color = None):
    image = drawLines(image, line_thickness, override_color = override_color)
    image = drawCircles(image, line_thickness=line_thickness, override_color=override_color)
    return image

def drawVisualTest(image):
    draw(img, line_thickness=4)
    applyBlooming(img, gausian_ksize=25, blur_ksize=25)
    applyBlooming(img)
    draw(img)
    applyBlooming(img)
    draw(img, override_color=WHITE, line_thickness=1)
    applyBlooming(img)
    draw(img, line_thickness=2)
    applyBlooming(img, gausian_ksize=3, blur_ksize=3)
    draw(img, line_thickness=1, override_color=WHITE)
    applyBlooming(img, gausian_ksize=3, blur_ksize=0)

img = createEmptyImage((1025, 768))

height, width = img.shape[:2]
center = (int(width/2), int(height/2))

#drawVisualTest(img)


img = drawTargetLines(img)
cv2.imshow('Test', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
cv2.waitKey()
