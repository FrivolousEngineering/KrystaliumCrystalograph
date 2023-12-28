import random
from PygameShader.shader import horizontal_glitch


class GlitchHandler:
    def __init__(self) -> None:
        self._glitch_counter = 0
        self._glitch_chance_per_tick = 5  # in percentage

    def update(self) -> None:
        if self._glitch_counter > 0:
            self._glitch_counter -= 1
        else:
            percentage_roll = random.random() * 100
            if percentage_roll < self._glitch_chance_per_tick:
                self.glitch()

    def glitch(self) -> None:
        self._glitch_counter += random.randint(15, 50)

    def draw(self, _screen) -> None:
        if self._glitch_counter:
            horizontal_glitch(_screen, 0.01, 0.08, self._glitch_counter % 5)
