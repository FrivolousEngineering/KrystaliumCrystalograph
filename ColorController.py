
from typing import Tuple, Dict

from FlickeringColor import FlickeringColor
Color = Tuple[int, int, int]


class ColorController:
    def __init__(self):
        self._colors: Dict[str, FlickeringColor] = {}
        self._colors["white"] = FlickeringColor(255, 255, 255)
        self._colors["black"] = FlickeringColor(0, 0, 0)
        self._colors["red"] = FlickeringColor(255, 0, 0)
        self._colors["blue"] = FlickeringColor(0, 0, 255)
        self._colors["green"] = FlickeringColor(0, 255, 0)
        self._colors["yellow"] = FlickeringColor(255, 255, 0)

    def getColor(self, color_name: str) -> Color:
        if color_name.lower() in self._colors:
            return self._colors[color_name.lower()].getRGB()
        return 255, 255, 255

    def update(self):
        for flickering_color in self._colors.values():
            flickering_color.update()