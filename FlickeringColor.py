import time
from datetime import datetime
from enum import Enum
from typing import Tuple
import numpy as np
import cv2
import random
import math


class FlickerState(Enum):
    BRIGHT = 1
    UP = 2
    DOWN = 3
    DIM = 4
    BRIGHT_HOLD = 5
    DIM_HOLD = 6


class FlickeringColor:
    def __init__(self, r: int, g: int, b: int, should_animate: bool = True) -> None:

        # Chance that the flicker will go to absolute_min_intensity instead of min_intensity
        self._drop_bottom_chance_percent = 10
        self._min_intensity = 200
        self._absolute_min_intensity = 128
        self._max_intensity = 255

        self._down_min_msecs = 20
        self._down_max_msecs = 250

        self._up_min_msecs = 20
        self._up_max_msecs = 250

        self._bright_hold_min_msecs = 0
        self._bright_hold_max_msecs = 100
        self._bright_hold_chance_percent = 50

        self._dim_hold_min_msecs = 0
        self._dim_hold_max_msecs = 50
        self._dim_hold_chance_percent = 5

        self._flicker_state: FlickerState = FlickerState.BRIGHT

        # When did the flicker start?
        self._flicker_start = 0
        # How long should the flicker last?
        self._flicker_msecs = 0

        self._intensity_start = 255
        self._intensity_end = 255

        self._r = r
        self._g = g
        self._b = b

        self._original_r = r
        self._original_g = g
        self._original_b = b

        self._start_time = datetime.utcnow()
        self._should_animate = should_animate

    def setFlicker(self, intensity: int) -> None:
        intensity = max(min(intensity, 255), 0)
        h, s, v = self.getOriginalHSV()
        self.setByHSV(h, s, intensity)


    @staticmethod
    def roundToInt(n) -> int:
        return math.floor(n + 0.5)

    def update(self) -> None:
        if not self._should_animate:
            return
        current_time = (datetime.utcnow() - self._start_time).total_seconds() * 1000
        match self._flicker_state:
            case FlickerState.BRIGHT:
                self._flicker_msecs = random.randint(self._down_min_msecs, self._down_max_msecs)
                self._flicker_start = current_time
                self._intensity_start = self._intensity_end

                if self._intensity_start > self._absolute_min_intensity and random.randint(0, 100) < self._drop_bottom_chance_percent:
                    # Drop to a value between the absolute min and the min intensity
                    self._intensity_end = random.randint(self._absolute_min_intensity, self._min_intensity)
                else:
                    # Find new value between min and current value
                    self._intensity_end = random.randint(self._min_intensity, self._intensity_start)
                self._flicker_state = FlickerState.DOWN
            case FlickerState.DIM:
                self._flicker_msecs = random.randint(self._up_min_msecs, self._up_max_msecs)
                self._flicker_start = current_time
                self._intensity_start = self._intensity_end
                self._intensity_end = random.randint(0, max(self._max_intensity - self._intensity_start, 0)) + self._min_intensity
                self._flicker_state = FlickerState.UP
            case FlickerState.DOWN | FlickerState.UP:
                if current_time < self._flicker_start + self._flicker_msecs:
                    self.setFlicker(self.roundToInt(self._intensity_start + ((self._intensity_end - self._intensity_start) * (((current_time - self._flicker_start) * 1.0) / self._flicker_msecs))))
                else:
                    self.setFlicker(self._intensity_end)
                    if self._flicker_state == FlickerState.DOWN:
                        if random.randint(0, 100) < self._dim_hold_chance_percent:
                            self._flicker_start = current_time
                            self._flicker_msecs = random.randint(self._dim_hold_min_msecs, self._dim_hold_max_msecs)
                            self._flicker_state = FlickerState.DIM_HOLD
                        else:
                            self._flicker_state = FlickerState.DIM
                    else:  # Flickerstate is UP
                        if random.randint(0, 100) < self._bright_hold_chance_percent:
                            self._flicker_start = current_time
                            self._flicker_msecs = random.randint(self._bright_hold_min_msecs, self._bright_hold_max_msecs)
                            self._flicker_state = FlickerState.BRIGHT_HOLD
                        else:
                            self._flicker_state = FlickerState.BRIGHT
            case FlickerState.BRIGHT_HOLD | FlickerState.DIM_HOLD:
                if current_time >= self._flicker_start + self._flicker_msecs:
                    self._flicker_state = FlickerState.BRIGHT if self._flicker_state == FlickerState.BRIGHT_HOLD else FlickerState.DIM

    def getRGB(self) -> Tuple[int, int, int]:
        return self._r, self._g, self._b

    def getOriginalRGB(self) -> Tuple[int, int, int]:
        return self._original_r, self._original_g, self._original_b

    def getHSV(self):
        hsv = cv2.cvtColor(np.uint8([[self.getRGB()]]), cv2.COLOR_RGB2HSV)
        return hsv[0][0][0], hsv[0][0][1], hsv[0][0][2]

    def getOriginalHSV(self):
        hsv = cv2.cvtColor(np.uint8([[self.getOriginalRGB()]]), cv2.COLOR_RGB2HSV)
        return hsv[0][0][0], hsv[0][0][1], hsv[0][0][2]

    def setByHSV(self, h, s, v):

        new_rgb = cv2.cvtColor(np.uint8([[(h, s, v)]]), cv2.COLOR_HSV2RGB)
        #print(type(new_rgb[0][0][0]))
        self._r = int(new_rgb[0][0][0])
        self._g = int(new_rgb[0][0][1])
        self._b = int(new_rgb[0][0][2])
        #BLUE = (int(blue_rgb[0][0][0] + 0.5), int(blue_rgb[0][0][1] + 0.5), int(blue_rgb[0][0][2] + 0.5))
        pass