import contextlib
import math
import random

# This suppresses the `Hello from pygame` message.
from Fader import Fader
from GlitchHandler import GlitchHandler
from MaskGenerator import MaskGenerator
from RFIDController import RFIDController
from SpikeGenerator import SpikeGenerator
from sql_app.schemas import Action, Target

with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import Crystalograph


def drawVerticalPatterns(crystalograph, inner_color, outer_color, inner_line_thickness, outer_line_thickness,
                         circle_radius, circle_shift, action_type: str = "random", target_type: str = "random",
                         line_type="double_line"):
    angle_difference = int(math.degrees(math.acos(circle_shift / circle_radius)))
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    spike_func = SpikeGenerator.getSpikeFunctionByTarget(target_type)
    mask_func = MaskGenerator.getMaskFunctionByAction(action_type)

    bottom_spikes = spike_func(-angle_difference, angle_difference)
    top_spikes = spike_func(180 - angle_difference, 180 + angle_difference)

    bottom_mask = mask_func(angle_difference, 360 - angle_difference)
    top_mask = mask_func(-180 + angle_difference, 180 - angle_difference)

    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                                begin_angle=-angle_difference,
                                end_angle=angle_difference,
                                base_color=inner_color, center=(center_x, center_y + circle_shift),
                                spikes=bottom_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                                begin_angle=angle_difference,
                                end_angle=360 - angle_difference,
                                base_color=outer_color, center=(center_x, center_y + circle_shift),
                                mask=bottom_mask)

    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                                begin_angle=180 - angle_difference, end_angle=180 + angle_difference,
                                base_color=inner_color, center=(center_x, center_y - circle_shift),
                                spikes=top_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                                begin_angle=-180 + angle_difference, end_angle=180 - angle_difference,
                                base_color=outer_color, center=(center_x, center_y - circle_shift),
                                mask=top_mask)


def drawHorizontalPatterns(crystalograph, inner_color, outer_color, inner_line_thickness, outer_line_thickness,
                           circle_radius, circle_shift, action_type: str = "random", target_type: str = "random",
                           line_type="double_line"):
    angle_difference = int(math.degrees(math.asin(circle_shift / circle_radius)))
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    spike_func = SpikeGenerator.getSpikeFunctionByTarget(target_type)
    mask_func = MaskGenerator.getMaskFunctionByAction(action_type)

    right_mask = mask_func(-angle_difference, 180 + angle_difference)
    left_mask = mask_func(180 - angle_difference, 360 + angle_difference)

    right_spikes = spike_func(180 + angle_difference, 360 - angle_difference)
    left_spikes = spike_func(angle_difference, 180 - angle_difference)

    # Right Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                                begin_angle=180 + angle_difference,
                                end_angle=360 - angle_difference,
                                base_color=inner_color,
                                center=(center_x + circle_shift, center_y),
                                spikes=right_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                                begin_angle=-angle_difference,
                                end_angle=180 + angle_difference,
                                base_color=outer_color,
                                center=(center_x + circle_shift, center_y),
                                mask=right_mask)

    # Left Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius,
                                begin_angle=angle_difference,
                                end_angle=180 - angle_difference,
                                base_color=inner_color,
                                center=(center_x - circle_shift, center_y),
                                spikes=left_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius,
                                begin_angle=180 - angle_difference,
                                end_angle=360 + angle_difference,
                                base_color=outer_color,
                                center=(center_x - circle_shift, center_y),
                                mask=left_mask)


def addLinesToCrystalopgrah(crystalograph, action_index, target_index):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2

    print("Positive:")
    drawHorizontalPatterns(crystalograph, "green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                           circle_shift, list(Action)[action_index], list(Target)[target_index])
    print("Negative:")
    drawVerticalPatterns(crystalograph, "green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                         circle_shift, list(Action)[action_index], list(Target)[target_index])


def addRandomLinesToCrystalograph(crystalograph):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2
    print("Positive:")
    drawHorizontalPatterns(crystalograph, "green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                           circle_shift)
    print("Negative:")
    drawVerticalPatterns(crystalograph, "green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
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
                addLinesToCrystalopgrah(crystalograph, target_index=current_target_index, action_index=current_action_index)
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
                cv2.imwrite(f"action_{list(Action)[current_action_index-1].value}_target_{list(Target)[current_target_index].value}.png", image)

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
