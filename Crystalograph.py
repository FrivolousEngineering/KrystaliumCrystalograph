from typing import Tuple

import numpy as np
import cv2
import math
# Typing helpers
Image = np.ndarray


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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

def drawCircleWithPolyLines(image, color, center, radius, segments, begin_angle = 0, end_angle = 90):
    assert segments >= 2, "We must have at least 2 segments"
    start_point = tuple(np.add(center, (0, -radius)))
    end_point = tuple(np.add(center, (radius, 0)))

    begin_angle_rad = math.radians(begin_angle + 180)
    end_angle_rad = math.radians(end_angle + 180)
    total_angle = end_angle_rad - begin_angle_rad


    spacing_between_angle = total_angle / (segments - 1)
    pts = []

    for segment in range(segments):
        extra = (-math.sin(segment * spacing_between_angle + begin_angle_rad) * radius, math.cos(segment * spacing_between_angle + begin_angle_rad) * radius)
        new_point = tuple(np.add(center, extra))

        pts.append(new_point)

    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1, 1, 2))
    image = cv2.polylines(image, [pts], False, color, 2)
    return image


img = createEmptyImage((1025, 768))
img = drawTargetLines(img)
height, width = img.shape[:2]
center = (int(width/2), int(height/2))
img = drawCircleWithPolyLines(img, BLUE, center, 100, 10, 0, 90)
img = drawCircleWithPolyLines(img, RED, center, 100, 10, 270, 360)
cv2.imshow('Test', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
cv2.waitKey()

