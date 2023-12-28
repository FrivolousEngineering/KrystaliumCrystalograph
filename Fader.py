import contextlib
# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame


class Fader:
    def __init__(self):
        self._fading = "in"
        self._alpha = 0
        sr = pygame.display.get_surface().get_rect()
        self._veil = pygame.Surface(sr.size)
        self._veil.fill((0, 0, 0))

    def fadeOut(self):
        self._fading = "out"

    def fadeIn(self):
        self._fading = "in"

    def draw(self, screen):
        if self._alpha > 0:
            self._veil.set_alpha(self._alpha)
            screen.blit(self._veil, (0, 0))

    def update(self):
        if self._fading == "in":
            if self._alpha > 0:
                self._alpha -= 1
        elif self._fading == "out":
            if self._alpha < 255:
                self._alpha += 1

        if self._alpha < 0:
            self._fading = None
            self._alpha = 0
        if self._alpha > 255:
            self._fading = None
            self._alpha = 255
