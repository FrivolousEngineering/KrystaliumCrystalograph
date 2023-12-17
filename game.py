import contextlib
import math
from typing import Tuple

# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import Crystalograph


if __name__ == '__main__':
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True
    crystalograph = Crystalograph.Crystalograph()

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
                                base_color="red", center=(center_x, center_y),
                                spikes = [(60, 20, 0.2),
                                          (10, 5, 0.2),
                                          (300, 25, 0.2)])

    #Outer
    crystalograph.addLineToDraw(line_type="line", thickness=5, radius=275, begin_angle=0, end_angle=360,
                                base_color="gree", center=(center_x, center_y),
                                spikes=[(80, 25, 0.15),
                                        (120, 5, 0.2),
                                        (150, 5, 0.15),
                                        (270, 25, 0.2)])

    crystalograph.setup()
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
                # Toggle fullscreen mode
                pygame.display.toggle_fullscreen()

        # This is where we insert the numpy array.
        # Because pygame and numpy use different coordinate systems,
        # the numpy image has to be flipped and rotated, before being blit.
        img = pygame.surfarray.make_surface(np.fliplr(np.rot90(image, k=-1)))
        screen.blit(img, (0, 0))

        pygame.display.flip()
        crystalograph.update()
        clock.tick()
        #print(clock.get_fps())

    pygame.quit()
