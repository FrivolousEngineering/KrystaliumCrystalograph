import contextlib
import random

# This suppresses the `Hello from pygame` message.
from Fader import Fader
from GlitchHandler import GlitchHandler
from RFIDController import RFIDController
from sql_app.schemas import Action, Target

with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import Crystalograph


def addLinesToCrystalopgrah(crystalograph, action_index, target_index):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2

    print("Positive:")
    crystalograph.drawHorizontalPatterns("green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                                         circle_shift, list(Action)[action_index], list(Target)[target_index])
    print("Negative:")
    crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift, list(Action)[action_index], list(Target)[target_index])


def addRandomLinesToCrystalograph(crystalograph):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2
    print("Positive:")
    crystalograph.drawHorizontalPatterns("green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                                         circle_shift)
    print("Negative:")
    crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift)


def onCardLost(card):
    print("Card lost", card)


def onCardDetected(card):
    print("Card Detected", card)


if __name__ == '__main__':
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True
    crystalograph = Crystalograph.Crystalograph()
    glitch_handler = GlitchHandler()
    rfid_controller = RFIDController(onCardDetected, onCardLost)
    rfid_controller.start()

    crystalograph.createEmptyImage((screen_width, screen_height))

    addRandomLinesToCrystalograph(crystalograph)

    crystalograph.setup()
    fader = Fader()
    screen_shake = 0
    current_action_index = 0
    current_target_index = 0

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
                screen_shake += 40
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                crystalograph.clearLinesToDraw()
                addRandomLinesToCrystalograph(crystalograph)
                crystalograph.setup()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                print("Increasing action")
                crystalograph.clearLinesToDraw()
                current_action_index += 1
                if current_action_index > 16:
                    current_action_index = 0
                addLinesToCrystalopgrah(crystalograph, target_index=current_target_index,
                                        action_index=current_action_index)
                crystalograph.setup()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                print("Increasing action")
                crystalograph.clearLinesToDraw()
                current_target_index += 1
                if current_target_index > 9:
                    current_target_index = 0
                addLinesToCrystalopgrah(crystalograph, target_index=current_target_index,
                                        action_index=current_action_index)
                crystalograph.setup()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                print("Saving")
                import cv2

                cv2.imwrite(
                    f"action_{list(Action)[current_action_index - 1].value}_target_{list(Target)[current_target_index].value}.png",
                    image)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                glitch_handler.glitch()

        if screen_shake:
            screen_displacement_x = random.random() * 4 - 2
            screen_displacement_y = random.random() * 4 - 2
            screen_shake -= 1
        else:
            screen_displacement_x = 0
            screen_displacement_y = 0

        fader.update()
        glitch_handler.update()

        # This is where we insert the numpy array.
        # Because pygame and numpy use different coordinate systems,
        # the numpy image has to be flipped and rotated, before being blit.
        img = pygame.surfarray.make_surface(np.fliplr(np.rot90(image, k=-1)))
        screen.blit(img, (screen_displacement_x, screen_displacement_y))

        fader.draw(screen)
        glitch_handler.draw(screen)

        pygame.display.flip()
        crystalograph.update()
        clock.tick()
        # print(clock.get_fps())

    pygame.quit()
