import contextlib
import math
import random

# This suppresses the `Hello from pygame` message.
from Fader import Fader
from GlitchHandler import GlitchHandler
from MaskGenerator import MaskGenerator

with contextlib.redirect_stdout(None):
    import pygame

import numpy as np
import Crystalograph


def generateSpikes1(start_angle, end_angle):
    half_angle = abs(end_angle - start_angle) / 2
    result = [(start_angle + half_angle, 40, 0.15),
              (start_angle + half_angle, 30, -0.05),
              (start_angle + half_angle, 15, -0.15),
              (start_angle + half_angle, 2, 0.2)]
    return result


def generateSpikes2(start_angle, end_angle):
    third_angle = abs(end_angle - start_angle) / 3
    result = [(start_angle + third_angle, 20, 0.05),
              (end_angle - third_angle, 20, -0.05)]
    return result


def generateSpikes3(start_angle, end_angle):
    third_angle = abs(end_angle - start_angle) / 3
    half_angle = abs(end_angle - start_angle) / 2
    result = [(start_angle + third_angle, 20, 0.05),
              (start_angle + half_angle, 20, -0.05),
              (end_angle - third_angle, 20, 0.05)]
    return result


def generateSpikes4(start_angle, end_angle):
    quarter_angle = abs(end_angle - start_angle) / 4
    third_angle = abs(end_angle - start_angle) / 3
    result = [(start_angle + quarter_angle, 20, 0.1),
              (start_angle + third_angle, 5, -0.1),
              (end_angle - third_angle, 5, -0.1),
              (end_angle - quarter_angle, 20, 0.1)]
    return result


def generateSpikes5(start_angle, end_angle):
    quarter_angle = abs(end_angle - start_angle) / 4
    third_angle = abs(end_angle - start_angle) / 3
    result = [(start_angle + quarter_angle, 5, -0.1),
              (start_angle + third_angle, 5, -0.1),
              (end_angle - third_angle, 5, -0.1),
              (end_angle - quarter_angle, 5, -0.1)]
    return result


def generateSpikes6(start_angle, end_angle):
    quarter_angle = abs(end_angle - start_angle) / 4
    third_angle = abs(end_angle - start_angle) / 3
    half_angle = abs(end_angle - start_angle) / 2
    result = [(start_angle + quarter_angle, 10, -0.1),
              (start_angle + third_angle, 10, -0.1),
              (start_angle + half_angle, 10, -0.15),
              (end_angle - third_angle, 10, -0.1),
              (end_angle - quarter_angle, 10, -0.1)]
    return result


def generateSpikes7(start_angle, end_angle):
    half_angle = abs(end_angle - start_angle) / 2
    result = [(start_angle + half_angle, half_angle, -0.15)]
    return result


def generateSpikes8(start_angle, end_angle):
    half_angle = abs(end_angle - start_angle) / 2
    result = [(start_angle + half_angle, half_angle, 0.15)]
    return result


def generateSpikes9(start_angle, end_angle):
    half_angle = abs(end_angle - start_angle) / 2
    quarter_angle = abs(end_angle - start_angle) / 4
    third_angle = abs(end_angle - start_angle) / 3
    result = [(start_angle + third_angle, quarter_angle, 0.05),
              (start_angle + quarter_angle, 5, -0.1),
              (start_angle + half_angle, third_angle, 0.15),
              (start_angle + half_angle, 5, -0.15),
              (end_angle - quarter_angle, 5, -0.1),
              (end_angle - third_angle, quarter_angle, 0.05)]
    return result


def generateSpikes10(start_angle, end_angle):
    half_angle = abs(end_angle - start_angle) / 2
    quarter_angle = abs(end_angle - start_angle) / 4

    result = [(start_angle + quarter_angle, 10, 0.15),
              (start_angle + half_angle, 10, -0.15),
              (end_angle - quarter_angle, 10, 0.15)]
    return result


def getRandomSpikeFunction():
    random_num = random.randint(1, 10)
    result = globals()[f"generateSpikes{random_num}"]
    print("Generated spike ", random_num)
    return result


def drawVerticalPatterns(crystalograph, inner_color, outer_color, inner_line_thickness, outer_line_thickness,
                         circle_radius, circle_shift, line_type="double_line"):
    angle_difference = int(math.degrees(math.acos(circle_shift / circle_radius)))
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    spike_func = getRandomSpikeFunction()
    mask_func = MaskGenerator.getRandomMaskFunction()

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
                           circle_radius, circle_shift, line_type="double_line"):
    angle_difference = int(math.degrees(math.asin(circle_shift / circle_radius)))
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    spike_func = getRandomSpikeFunction()
    pattern_func = MaskGenerator.getRandomMaskFunction()

    right_mask = pattern_func(-angle_difference, 180 + angle_difference)
    left_mask = pattern_func(180 - angle_difference, 360 + angle_difference)

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


def addRandomLinesToCrystalograph(crystalograph):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2
    drawHorizontalPatterns(crystalograph, "green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                           circle_shift)
    drawVerticalPatterns(crystalograph, "green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                         circle_shift)


if __name__ == '__main__':
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True
    crystalograph = Crystalograph.Crystalograph()
    glitch_handler = GlitchHandler()

    crystalograph.createEmptyImage((screen_width, screen_height))

    addRandomLinesToCrystalograph(crystalograph)

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
                screen_shake += 40
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                crystalograph.clearLinesToDraw()
                addRandomLinesToCrystalograph(crystalograph)
                crystalograph.setup()

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
