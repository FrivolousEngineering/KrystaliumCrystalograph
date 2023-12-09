import contextlib
from typing import Tuple

# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import blooming


def image_generator(size: Tuple[int, int], color: blooming.Colors):
    image = np.zeros((*size[::-1], 3), dtype=np.uint8)

    # Create the glowing border, and a copy of the image, for the text, that will be placed on it later.
    border = blooming.glowing_border(image.copy(), color=color)
    text = image.copy()

    # This message will be incrementally written
    message = "Welcome to this game. Don't be scared :)." + " " * 10

    for idx in range(len(message) + 1):
        text = blooming.glowing_text(image.copy(), text=message[:idx], org=(50, 70), color=color)
        yield np.bitwise_or(border, text)
    return np.bitwise_or(border, text)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    running = True

    while running:
        for image in image_generator(screen.get_size(), color=blooming.Colors.YELLOW_ISH):
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
