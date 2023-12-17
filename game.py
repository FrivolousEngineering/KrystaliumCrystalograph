import contextlib
from typing import Tuple

# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import Crystalograph



if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    clock = pygame.time.Clock()
    running = True
    crystalograph = Crystalograph.Crystalograph()
    crystalograph.createEmptyImage((1024, 768))

    crystalograph.addLineToDraw(line_type="line", thickness=2, radius=150, begin_angle=185, end_angle=209,
                                base_color="blue", center=crystalograph._center)
    crystalograph.addLineToDraw(line_type="line", thickness=2, radius=200, begin_angle=185, end_angle=209,
                                base_color="red", center=crystalograph._center)
    crystalograph.addLineToDraw(line_type="line", thickness=2, radius=300, begin_angle=185, end_angle=209,
                                base_color="red", center=crystalograph._center)

    crystalograph.addLineToDraw(line_type="line", thickness=2, radius=300, begin_angle=0, end_angle=90,
                                base_color="green", center=crystalograph._center)

    crystalograph.setup()
    while running:
        crystalograph.createEmptyImage((1024, 768))
        image = crystalograph.draw()
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # This is where we insert the numpy array.
        # Because pygame and numpy use different coordinate systems,
        # the numpy image has to be flipped and rotated, before being blit.
        img = pygame.surfarray.make_surface(np.fliplr(np.rot90(image, k=-1)))
        screen.blit(img, (0, 0))

        pygame.display.flip()
        crystalograph.update()
        clock.tick(np.random.randint(10, 30))

    pygame.quit()
