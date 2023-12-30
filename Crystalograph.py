from typing import Tuple, Optional, List

import numpy as np
import cv2
import math

from ColorController import ColorController
from DisplayLine import DisplayLine, Spike

from functools import cache

# Typing helpers
from DoubleDisplayLine import DoubleDisplayLine
from MaskGenerator import MaskGenerator
from SpikeGenerator import SpikeGenerator

Image = np.ndarray
Point = Tuple[int, int]
Color = Tuple[int, int, int]

NUM_SEGMENTS_PER_LENGTH = 0.4
NUM_BACKGROUND_IMAGES = 48


class Crystalograph:
    def __init__(self) -> None:
        self._image: Optional[np.ndarray] = None
        self._center = (0, 0)
        self._width = 0
        self._height = 0
        self._lines_to_draw = []
        self._color_controller = ColorController()

        # Speed option. Keep the base layer in memory so a re-draw isn't needed.
        self._base_layer_image: Optional[np.ndarray] = None
        self._counter = 0  # Used to trick the drawBackground cache into giving different images

    def addLineToDraw(self, line_type: str, base_color: str, radius: int, thickness: int, center: Point,
                      begin_angle: int, end_angle: int, spikes: Optional[List[Spike]] = None,
                      mask: Optional[List] = None):
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
        self._base_layer_image = None

    def _createBaseImage(self, size: Tuple[int, int]) -> None:
        self._base_layer_image = np.zeros((*size[::-1], 3), dtype=np.uint8)

    def clearLinesToDraw(self):
        self._lines_to_draw = []

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

    def applyBlooming(self, target_image, gaussian_ksize: int = 9, blur_ksize: int = 5) -> None:
        # Provide some blurring to image, to create some bloom.
        if gaussian_ksize > 0:
            cv2.GaussianBlur(target_image, (gaussian_ksize, gaussian_ksize), 0, dst=target_image)
        if blur_ksize > 0:
            cv2.blur(target_image, ksize=(blur_ksize, blur_ksize), dst=target_image)

    @cache
    def _drawBaseImage(self, variation):
        if self._base_layer_image is not None:
            return self._base_layer_image

        self._createBaseImage((self._width, self._height))
        for line in self._lines_to_draw:
            self._base_layer_image = line.draw(self._image, thickness_modifier=2, noise_modifier=0,
                                    override_color="pale_" + line._color_name)

        # Some nice blurring
        self.applyBlooming(self._base_layer_image, gaussian_ksize=25, blur_ksize=25)
        return self._base_layer_image
    
    def draw(self) -> np.ndarray:
        # Cache the background image that gives the glow
        background = self._drawBaseImage(self._counter)

        self.createEmptyImage((self._width, self._height))
        # Draw the lines again so that there is a difference between the blur and the line itself
        for line in self._lines_to_draw:
            line.draw(self._image)

        # Draw a white line over it for the highlight
        kernel = np.ones((5, 5), np.uint8)

        # Convert to black & white image
        highlights = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        highlights = cv2.cvtColor(highlights, cv2.COLOR_GRAY2RGB)

        # We want to do higlights. Whooo
        cv2.erode(highlights, kernel, highlights)

        # Merge em together again
        image_with_background = cv2.addWeighted(background, 1, self._image, 1, 0)

        self._counter += 1

        if self._counter > NUM_BACKGROUND_IMAGES:
            self._counter = 0
        result = cv2.addWeighted(highlights, 3, image_with_background, 1, 0)

        self.applyBlooming(result, gaussian_ksize=0, blur_ksize=3)
        return result

    def setup(self) -> None:
        for line in self._lines_to_draw:
            line.setColorController(self._color_controller)
            line.setup()
        self._base_layer_image = None
        self._drawBaseImage.cache_clear()

    def update(self) -> None:
        self._color_controller.update()

    def drawHorizontalPatterns(self, inner_color, outer_color, inner_line_thickness, outer_line_thickness,
                               circle_radius, circle_shift, action_type: str = "random", target_type: str = "random",
                               line_type="double_line"):
        angle_difference = int(math.degrees(math.asin(circle_shift / circle_radius)))
        center_x = int(self._width / 2)
        center_y = int(self._height / 2)

        spike_func = SpikeGenerator.getSpikeFunctionByTarget(target_type)
        mask_func = MaskGenerator.getMaskFunctionByAction(action_type)

        right_mask = mask_func(-angle_difference, 180 + angle_difference)
        left_mask = mask_func(180 - angle_difference, 360 + angle_difference)

        right_spikes = spike_func(180 + angle_difference, 360 - angle_difference)
        left_spikes = spike_func(angle_difference, 180 - angle_difference)

        # Right Circle
        self.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                           begin_angle=180 + angle_difference,
                           end_angle=360 - angle_difference,
                           base_color=inner_color,
                           center=(center_x + circle_shift, center_y),
                           spikes=right_spikes)
        self.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                           begin_angle=-angle_difference,
                           end_angle=180 + angle_difference,
                           base_color=outer_color,
                           center=(center_x + circle_shift, center_y),
                           mask=right_mask)

        # Left Circle
        self.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                           begin_angle=angle_difference,
                           end_angle=180 - angle_difference,
                           base_color=inner_color,
                           center=(center_x - circle_shift, center_y),
                           spikes=left_spikes)
        self.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                           begin_angle=180 - angle_difference,
                           end_angle=360 + angle_difference,
                           base_color=outer_color,
                           center=(center_x - circle_shift, center_y),
                           mask=left_mask)

    def drawVerticalPatterns(self, inner_color, outer_color, inner_line_thickness, outer_line_thickness,
                             circle_radius, circle_shift, action_type: str = "random", target_type: str = "random",
                             line_type="double_line"):
        angle_difference = int(math.degrees(math.acos(circle_shift / circle_radius)))
        center_x = int(self._width / 2)
        center_y = int(self._height / 2)

        spike_func = SpikeGenerator.getSpikeFunctionByTarget(target_type)
        mask_func = MaskGenerator.getMaskFunctionByAction(action_type)

        bottom_spikes = spike_func(-angle_difference, angle_difference)
        top_spikes = spike_func(180 - angle_difference, 180 + angle_difference)

        bottom_mask = mask_func(angle_difference, 360 - angle_difference)
        top_mask = mask_func(-180 + angle_difference, 180 - angle_difference)

        self.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                           begin_angle=-angle_difference,
                           end_angle=angle_difference,
                           base_color=inner_color, center=(center_x, center_y + circle_shift),
                           spikes=bottom_spikes)
        self.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                           begin_angle=angle_difference,
                           end_angle=360 - angle_difference,
                           base_color=outer_color, center=(center_x, center_y + circle_shift),
                           mask=bottom_mask)

        self.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                           begin_angle=180 - angle_difference, end_angle=180 + angle_difference,
                           base_color=inner_color, center=(center_x, center_y - circle_shift),
                           spikes=top_spikes)
        self.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                           begin_angle=-180 + angle_difference, end_angle=180 - angle_difference,
                           base_color=outer_color, center=(center_x, center_y - circle_shift),
                           mask=top_mask)


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
