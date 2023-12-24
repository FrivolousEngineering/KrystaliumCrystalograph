from typing import Tuple, Optional, List

import numpy as np
import cv2

from ColorController import ColorController
from DisplayLine import DisplayLine, Spike

# Typing helpers
from DoubleDisplayLine import DoubleDisplayLine

Image = np.ndarray
Point = Tuple[int, int]
Color = Tuple[int, int, int]

NUM_SEGMENTS_PER_LENGTH = 0.4


class Crystalograph:
    def __init__(self) -> None:
        self._image: Optional[np.ndarray] = None
        self._center = (0, 0)
        self._width = 0
        self._height = 0
        self._lines_to_draw = []
        self._color_controller = ColorController()

    def addLineToDraw(self, line_type: str, base_color: str, radius: int, thickness: int, center: Point,
                      begin_angle: int, end_angle: int, spikes: Optional[List[Spike]] = None, mask: Optional[List] = None):
        data = locals()
        del data["self"]
        if line_type == "line":
            self._lines_to_draw.append(DisplayLine(**data))
        if line_type == "double_line":
            self._lines_to_draw.append(DoubleDisplayLine(**data))

    def createEmptyImage(self, size: Tuple[int, int]) -> None:
        self._image = np.zeros((*size[::-1], 3), dtype=np.uint8)
        self._height, self._width = self._image.shape[:2]
        self._center = (int(self._width / 2), int(self._height / 2))

    def drawTargetLines(self) -> None:
        """
        Draw the horizontal & vertical target line
        """
        # Numpy uses the convention `rows, columns`, instead of `x, y`.
        # Therefore, height has to be before width.
        width = self._width
        height = self._height

        line_color = self._color_controller.getColor("normal_white")
        cv2.line(self._image, (int(width / 2), 0), (int(width / 2), height), line_color, 1)
        cv2.line(self._image, (0, int(height / 2)), (width, int(height / 2)), line_color, 1)

    def applyBlooming(self, gaussian_ksize: int = 9, blur_ksize: int = 5) -> None:
        # Provide some blurring to image, to create some bloom.
        if gaussian_ksize > 0:
            cv2.GaussianBlur(self._image, (gaussian_ksize, gaussian_ksize), 0, dst=self._image)
        if blur_ksize > 0:
            cv2.blur(self._image, ksize=(blur_ksize, blur_ksize), dst=self._image)

    def draw(self) -> np.ndarray:
        # Draw all the lines
        for line in self._lines_to_draw:
            self._image = line.draw(self._image, thickness_modifier=2, noise_modifier=0)

        # Some nice blurring
        self.applyBlooming(gaussian_ksize=25, blur_ksize=25)

        self.applyBlooming()
        for line in self._lines_to_draw:
            self._image = line.draw(self._image)
        for line in self._lines_to_draw:
            self._image = line.draw(self._image, override_color="white", thickness_modifier=0.2, noise_modifier=1.2)

        self.applyBlooming(0, 3)
        # self.drawTargetLines()
        return self._image

    def setup(self) -> None:
        for line in self._lines_to_draw:
            line.setColorController(self._color_controller)
            line.setup()

    def update(self) -> None:
        self._color_controller.update()


if __name__ == '__main__':
    crystalograph = Crystalograph()
    crystalograph.createEmptyImage((1024, 768))

    crystalograph.addLineToDraw(line_type="line", thickness=1, radius=150, begin_angle=185, end_angle=209,
                                base_color="blue", center=crystalograph._center)
    crystalograph.addLineToDraw(line_type="line", thickness=1, radius=200, begin_angle=185, end_angle=209,
                                base_color="blue", center=crystalograph._center)
    crystalograph.addLineToDraw(line_type="line", thickness=1, radius=300, begin_angle=185, end_angle=209,
                                base_color="blue", center=crystalograph._center)

    crystalograph.addLineToDraw(line_type="double_line", thickness=1, radius=300, begin_angle=185, end_angle=209,
                                base_color="blue", center=crystalograph._center)

    crystalograph.setup()
    img = crystalograph.draw()
    cv2.imshow('Test', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey()
