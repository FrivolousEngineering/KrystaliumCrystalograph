from typing import Tuple, Dict

from FlickeringColor import FlickeringColor
Color = Tuple[int, int, int]


class ColorController:
    def __init__(self):
        self._colors: Dict[str, FlickeringColor] = {}
        self._colors["white"] = FlickeringColor(255, 255, 255)
        self._colors["black"] = FlickeringColor(0, 0, 0)
        self._colors["red"] = FlickeringColor(255, 0, 0)
        self._colors["red_2"] = FlickeringColor(255, 0, 0)
        self._colors["blue"] = FlickeringColor(0, 0, 255)
        self._colors["blue_2"] = FlickeringColor(0, 0, 255)
        self._colors["pale_blue"] = FlickeringColor(128, 128, 255)
        self._colors["pale_blue_2"] = FlickeringColor(128, 128, 255)
        self._colors["pale_green"] = FlickeringColor(128, 255, 128)
        self._colors["dark_green"] = FlickeringColor(0, 255, 0, min_intensity=100, absolute_min_intensity=64, max_intensity=128)
        self._colors["dark_blue"] = FlickeringColor(0, 0, 255, min_intensity=100, absolute_min_intensity=64, max_intensity=128)
        self._colors["dark_green_2"] = FlickeringColor(0, 255, 0, min_intensity=100, absolute_min_intensity=64,
                                                     max_intensity=128)
        self._colors["dark_blue_2"] = FlickeringColor(0, 0, 255, min_intensity=100, absolute_min_intensity=64,
                                                    max_intensity=128)
        self._colors["pale_red"] = FlickeringColor(255, 128, 128)
        self._colors["pale_red_2"] = FlickeringColor(255, 128, 128)
        self._colors["blue_3"] = FlickeringColor(0, 0, 255)
        self._colors["light_blue"] = FlickeringColor(173, 216, 230)
        self._colors["green"] = FlickeringColor(0, 255, 0)
        self._colors["green_2"] = FlickeringColor(0, 255, 0)
        self._colors["pale_green_2"] = FlickeringColor(128, 255, 128)
        self._colors["yellow"] = FlickeringColor(255, 255, 0)

    def getColor(self, color_name: str) -> Color:
        if color_name.lower() in self._colors:
            return self._colors[color_name.lower()].getRGB()
        return 0, 0, 0

    def update(self):
        for flickering_color in self._colors.values():
            flickering_color.update()
