import numpy
import cv2

from DisplayLine import DisplayLine


class DoubleDisplayLine(DisplayLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        pass

    def draw(self, image, override_color: None = None, alpha=1.0, thickness_modifier: float = 1.0, noise_modifier: float = 1.0):

        thickness_to_use = thickness_modifier * self._thickness
        pts_top = self.generateCirclePolyLines(self._center, int(self._radius - thickness_to_use / 2), self._begin_angle,
                                               self._end_angle,
                                               noise=noise_modifier * self._noise,)

        pts_bottom = self.generateCirclePolyLines(self._center, int(self._radius + thickness_to_use / 2), self._begin_angle,
                                                  self._end_angle,
                                                  noise=noise_modifier * self._noise)

        # Due to winding order, we need to flip the bottom points again
        pts_bottom = numpy.flipud(pts_bottom)
        pts = numpy.append(pts_top, pts_bottom)

        pts = pts.reshape((-1, 1, 2))

        color_to_use = self._color_controller.getColor(self._color_name)
        if override_color is not None:
            color_to_use = self._color_controller.getColor(override_color)

        if alpha < 1.0:
            overlay = image.copy()
            cv2.fillPoly(overlay, [pts], color_to_use)
            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        else:
            # Actually draw them
            image = cv2.fillPoly(image, [pts], color_to_use)
        return image
