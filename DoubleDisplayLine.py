import numpy
import cv2
import numpy as np

from DisplayLine import DisplayLine


class DoubleDisplayLine(DisplayLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        pass

    def draw(self, image, override_color: None = None, alpha=1.0, thickness_modifier: float = 1.0, noise_modifier: float = 1.0, disable_mask: bool = False):

        thickness_to_use = thickness_modifier * self._thickness
        pts_top = self.generateCirclePolyLines(self._center, int(self._radius - thickness_to_use / 2), self._begin_angle,
                                               self._end_angle,
                                               noise=noise_modifier * self._noise,)

        pts_bottom = self.generateCirclePolyLines(self._center, int(self._radius + thickness_to_use / 2), self._begin_angle,
                                                  self._end_angle,
                                                  noise=noise_modifier * self._noise)

        if self._angle_noise:
            # Re-create the mask if you want noise on the angle, otherwise just keep the default
            self._mask_array = self._generateMask()

        if self._mask and not disable_mask:
            masked_bottom_array = self._maskArray(pts_bottom, self._mask_array)
            masked_top_array = self._maskArray(pts_top, self._mask_array)

            segments = np.ma.clump_unmasked(masked_top_array)

            final_points_top = []
            final_points_bottom = []
            for segment in segments:
                # The segments are based on the flattened array. By just dividing it by 2, we get the right result
                # Previously I would flatten & reshape, but that is *much* more expensive...
                modified_segment = slice(int(segment.start / 2), int(segment.stop / 2))
                final_points_top.append(masked_top_array[modified_segment])
                final_points_bottom.append(masked_bottom_array[modified_segment])
        else:
            final_points_top = [pts_top]
            final_points_bottom = [pts_bottom]

        color_to_use = self._color_controller.getColor(self._color_name)
        if override_color is not None:
            color_to_use = self._color_controller.getColor(override_color)

        if alpha < 1.0:
            overlay = image.copy()
            for bottom_points, top_points in zip(final_points_bottom, final_points_top):
                pts_bottom = numpy.flipud(bottom_points)
                pts = numpy.concatenate((top_points, pts_bottom))
                cv2.fillPoly(overlay, [pts], color_to_use)
            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        else:
            # Actually draw them
            for bottom_points, top_points in zip(final_points_bottom, final_points_top):
                pts_bottom = numpy.flipud(bottom_points)
                pts = numpy.concatenate((top_points, pts_bottom))
                image = cv2.fillPoly(image, [pts], color_to_use)
        return image
