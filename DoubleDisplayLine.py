import numpy
import cv2
import numpy as np

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

        if self._angle_noise:
            # Re-create the mask if you want noise on the angle, otherwise just keep the default
            self._mask_array = self._generateMask()

        if self._mask:
            masked_bottom_array = self._maskArray(pts_bottom, self._mask_array)
            masked_top_array = self._maskArray(pts_top, self._mask_array)

            segments = np.ma.clump_unmasked(masked_top_array)

            # We need to flatten the array, because clump_unmask doesn't work on anything but 1d arrays.
            # When we add the points to the final list we can reshape them again...
            flattend_masked_bottom_array = masked_bottom_array.flatten()
            flattend_masked_top_array = masked_top_array.flatten()

            final_points_top = []
            final_points_bottom = []
            for segment in segments:
                final_points_top.append(np.reshape(flattend_masked_top_array[segment], (-1, 2)))
                final_points_bottom.append(np.reshape(flattend_masked_bottom_array[segment], (-1, 2)))
        else:
            #pts = pts.reshape((-1, 1, 2))
            final_points_top = [pts_top]
            final_points_bottom = [pts_bottom]


        # Due to winding order, we need to flip the bottom points again
        #pts_bottom = numpy.flipud(pts_bottom)
        #pts = numpy.append(pts_top, pts_bottom)

        #pts = pts.reshape((-1, 1, 2))

        color_to_use = self._color_controller.getColor(self._color_name)
        if override_color is not None:
            color_to_use = self._color_controller.getColor(override_color)

        if alpha < 1.0:
            overlay = image.copy()
            for bottom_points, top_points in zip(final_points_bottom, final_points_top):
                pts_bottom = numpy.flipud(bottom_points)
                pts = numpy.append(top_points, pts_bottom)

                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(overlay, [pts], color_to_use)
            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        else:
            # Actually draw them
            for bottom_points, top_points in zip(final_points_bottom, final_points_top):
                pts_bottom = numpy.flipud(bottom_points)
                pts = numpy.append(top_points, pts_bottom)

                pts = pts.reshape((-1, 1, 2))
                image = cv2.fillPoly(image, [pts], color_to_use)
        return image
