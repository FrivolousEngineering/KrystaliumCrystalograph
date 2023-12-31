import contextlib
# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame


class Fader:
    def __init__(self):
        self._fading = None
        self._alpha = 255
        sr = pygame.display.get_surface().get_rect()
        self._veil = pygame.Surface(sr.size)
        self._veil.fill((0, 0, 0))
        self._fader_speed = 3

    def isFading(self):
        return self._fading is not None

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
                self._alpha -= self._fader_speed
        elif self._fading == "out":
            if self._alpha < 255:
                self._alpha += self._fader_speed

        if self._alpha <= 0:
            self._fading = None
            self._alpha = 0
        if self._alpha >= 255:
            self._fading = None
            self._alpha = 255
