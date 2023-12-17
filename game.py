import contextlib
import math
import random
from typing import Tuple

# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame

import PygameShader
from PygameShader.shader import horizontal_glitch

import numpy as np
import Crystalograph


class Fader:
    def __init__(self):
        self._fading = "in"
        self._alpha = 255
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


if __name__ == '__main__':
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True
    crystalograph = Crystalograph.Crystalograph()
    frame = 0
    glitching = 0
    crystalograph.createEmptyImage((screen_width, screen_height))

    center_x = screen_width/2
    center_y = screen_height / 2

    # Inner & outer alignment lines
    crystalograph.addLineToDraw(line_type="line", thickness=1, radius=350, begin_angle=0, end_angle=360,
                                base_color="blue", center=(center_x, center_y))
    crystalograph.addLineToDraw(line_type="line", thickness=1, radius=30, begin_angle=0, end_angle=360,
                                base_color="blue", center=(center_x, center_y))

    # Inner
    crystalograph.addLineToDraw(line_type="line", thickness=5, radius=75, begin_angle=0, end_angle=360,
                                base_color="blue", center=(center_x, center_y),
                                spikes=[(60, 20, 0.2),
                                        (120, 5, 0.2),
                                        (300, 25, 0.2)])

    #Middle
    crystalograph.addLineToDraw(line_type="line", thickness=5, radius=175, begin_angle=0, end_angle=360,
                                base_color="blue_2", center=(center_x, center_y),
                                spikes = [(60, 20, 0.2),
                                          (10, 5, 0.2),
                                          (300, 25, 0.2)])

    #Outer
    crystalograph.addLineToDraw(line_type="line", thickness=5, radius=275, begin_angle=0, end_angle=360,
                                base_color="blue_3", center=(center_x, center_y),
                                spikes=[(80, 25, 0.15),
                                        (120, 5, 0.2),
                                        (150, 5, 0.15),
                                        (270, 25, 0.2)])

    crystalograph.setup()
    fader = Fader()
    screen_shake = 0

    while running:
        crystalograph.createEmptyImage((screen_width, screen_height))
        image = crystalograph.draw()
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                fader.fadeIn()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                fader.fadeOut()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                screen_shake += 1

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                glitching += 20

        if screen_shake:
            screen_displacement_x = random.randint(0, 8) - 4
            screen_displacement_y = random.randint(0, 8) - 4
            screen_shake -= 1
        else:
            screen_displacement_x = 0
            screen_displacement_y = 0


        fader.update()

        # This is where we insert the numpy array.
        # Because pygame and numpy use different coordinate systems,
        # the numpy image has to be flipped and rotated, before being blit.
        img = pygame.surfarray.make_surface(np.fliplr(np.rot90(image, k=-1)))
        screen.blit(img, (screen_displacement_x, screen_displacement_y))
        fader.draw(screen)

        if glitching:
            horizontal_glitch(screen, 0.01, 0.08, glitching % 6)
            glitching -= 1

        frame += 1

        pygame.display.flip()
        crystalograph.update()
        clock.tick()
        #print(clock.get_fps())

    pygame.quit()
