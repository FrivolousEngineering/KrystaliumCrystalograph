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

    while running:
        image = Crystalograph.createEmptyImage((1024, 768))
        image = Crystalograph.drawVisualTest(image)
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
        clock.tick(np.random.randint(10, 30))

    pygame.quit()
