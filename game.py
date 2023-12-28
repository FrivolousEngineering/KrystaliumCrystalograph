import contextlib
import math
import random

# This suppresses the `Hello from pygame` message.
with contextlib.redirect_stdout(None):
    import pygame

from PygameShader.shader import horizontal_glitch

import numpy as np
import Crystalograph


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


class GlitchHandler:
    def __init__(self) -> None:
        self._glitch_counter = 0
        self._glitch_chance_per_tick = 5  # in percentage

    def update(self) -> None:
        if self._glitch_counter > 0:
            self._glitch_counter -= 1
        else:
            percentage_roll = random.random() * 100
            if percentage_roll < self._glitch_chance_per_tick:
                self.glitch()

    def glitch(self) -> None:
        self._glitch_counter += random.randint(15, 50)

    def draw(self, _screen) -> None:
        if self._glitch_counter:
            horizontal_glitch(_screen, 0.01, 0.08, self._glitch_counter % 5)


def generateAngles(spacing, angle_width, start_angle=0, end_angle=360, shift=0):
    angle_to_add = start_angle + 0.5 * angle_width
    result = []
    while angle_to_add < end_angle + 0.5 * angle_width:
        result.append((angle_to_add, angle_width))
        angle_to_add += spacing
    return result


def generatePattern1(start_angle, end_angle):
    result = []
    result.extend(generateAngles(30, 10, start_angle, end_angle))
    result.extend(generateAngles(15, 5, start_angle, end_angle))
    result.extend(generateAngles(60, 20, start_angle, end_angle))
    return result


def generatePattern2(start_angle, end_angle):
    result = []
    result.extend(generateAngles(15, 5, start_angle, end_angle))
    result.extend(generateAngles(16, 10, start_angle, end_angle))
    return result


def generatePattern3(start_angle, end_angle):
    result = []
    result.extend(generateAngles(15, 5, start_angle, end_angle))
    result.extend(generateAngles(16, 5, start_angle, end_angle))
    return result


def generatePattern4(start_angle, end_angle):
    result = []
    result.extend(generateAngles(30, 5, start_angle, end_angle))
    result.extend(generateAngles(30, 5, start_angle, end_angle))
    result.extend(generateAngles(40, 5, start_angle, end_angle))
    result.extend(generateAngles(50, 5, start_angle, end_angle))
    return result


def generatePattern5(start_angle, end_angle):
    result = []
    result.extend(generateAngles(20, 10, start_angle, end_angle))
    result.extend(generateAngles(30, 15, start_angle, end_angle))
    return result


def generatePattern6(start_angle, end_angle):
    result = []
    result.extend(generateAngles(60, 10, start_angle, end_angle))
    result.extend(generateAngles(70, 10, start_angle, end_angle))
    return result


def generatePattern7(start_angle, end_angle):
    result = []
    result.extend(generateAngles(15, 2, start_angle, end_angle))
    result.extend(generateAngles(20, 3, start_angle, end_angle))
    return result


def generatePattern8(start_angle, end_angle):
    result = []
    result.extend(generateAngles(15, 2, start_angle, end_angle))
    result.extend(generateAngles(20, 3, start_angle, end_angle))
    result.extend(generateAngles(25, 3, start_angle, end_angle))
    return result


def generatePattern9(start_angle, end_angle):
    result = []
    result.extend(generateAngles(30, 10, start_angle + 10, end_angle))
    result.extend(generateAngles(60, 15, start_angle + 20, end_angle))
    result.extend(generateAngles(15, 2, start_angle + 10, end_angle))
    return result


def generatePattern10(start_angle, end_angle):
    result = []
    result.extend(generateAngles(10, 5, start_angle, start_angle + 60 + 5))
    result.extend(generateAngles(20, 10, start_angle + 60, end_angle - 60))
    result.extend(generateAngles(10, 5, end_angle - 60, end_angle))
    return result


def generatePattern11(start_angle, end_angle):
    result = []
    result.extend(generateAngles(20, 10, start_angle, start_angle + 60 + 5))
    result.extend(generateAngles(10, 5, start_angle + 60, end_angle - 60))
    result.extend(generateAngles(20, 10, end_angle - 60, end_angle))
    return result


def generatePattern12(start_angle, end_angle):
    result = []
    result.extend(generateAngles(15, 10, start_angle, start_angle + 60 + 5))
    result.extend(generateAngles(8, 5, start_angle + 60, end_angle - 60))
    result.extend(generateAngles(15, 10, end_angle - 60, end_angle))
    return result


def generatePattern13(start_angle, end_angle):
    result = []
    result.extend(generateAngles(8, 5, start_angle, start_angle + 60 + 5))
    result.extend(generateAngles(15, 10, start_angle + 60, end_angle - 60))
    result.extend(generateAngles(8, 5, end_angle - 60, end_angle))
    return result


def generatePattern14(start_angle, end_angle):
    result = []
    half_angle = abs(end_angle - start_angle) / 2
    result.extend(generateAngles(12, 6, start_angle, start_angle + half_angle))
    result.extend(generateAngles(22, 11, start_angle + half_angle, end_angle))
    return result


def generatePattern15(start_angle, end_angle):
    result = []
    half_angle = abs(end_angle - start_angle) / 2
    result.extend(generateAngles(22, 11, start_angle, start_angle + half_angle))
    result.extend(generateAngles(12, 6, start_angle + half_angle, end_angle))
    return result


def generatePattern16(start_angle, end_angle):
    result = []
    result.extend(generateAngles(4, 2, start_angle, end_angle))
    return result


def generatePattern17(start_angle, end_angle):
    result = []
    result.extend(generateAngles(8, 4, start_angle, end_angle))
    result.extend(generateAngles(4, 2, start_angle, end_angle))
    return result


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


def getRandomPatternFunction():
    random_num = random.randint(1, 17)
    result = globals()[f"generatePattern{random_num}"]
    print("Generated pattern ", random_num)
    return result


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

    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    circle_shift = 125

    circle_shift_horizontal = circle_shift
    circle_shift_vertical = circle_shift
    circle_radius = 200

    circle_radius_horizontal = circle_radius
    circle_radius_vertical = circle_radius

    angle_difference = int(math.degrees(math.asin(circle_shift_horizontal / circle_radius_horizontal)))

    angle_difference_2 = int(math.degrees(math.acos(circle_shift_vertical / circle_radius_vertical)))
    line_type = "double_line"

    spike_func_horizontal = getRandomSpikeFunction()
    spike_func_vertical = getRandomSpikeFunction()

    right_spikes = spike_func_horizontal(180 + angle_difference, 360 - angle_difference)
    left_spikes = spike_func_horizontal(angle_difference, 180 - angle_difference)
    bottom_spikes = spike_func_vertical(-angle_difference_2, angle_difference_2)
    top_spikes = spike_func_vertical(180 - angle_difference_2, 180 + angle_difference_2)

    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2

    pattern_func_horizontal = getRandomPatternFunction()
    pattern_func_vertical = getRandomPatternFunction()

    right_mask = pattern_func_horizontal(-angle_difference, 180 + angle_difference)
    left_mask = pattern_func_horizontal(180 - angle_difference, 360 + angle_difference)

    bottom_mask = pattern_func_vertical(angle_difference_2, 360 - angle_difference_2)
    top_mask = pattern_func_vertical(-180 + angle_difference_2, 180 - angle_difference_2)

    inner_color = "green"
    horizontal_inner_color = inner_color
    vertical_inner_color = inner_color + "_2"

    outer_color = "blue"
    horizontal_outer_color = outer_color
    vertical_outer_color = outer_color + "_2"

    # top_mask.extend(generateAngles(115, 40, -180 + angle_difference_2, 180 - angle_difference_2))
    # top_mask = [] # generateAngles(15, 10, -180 + angle_difference_2, 180 - angle_difference_2)

    # Right Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius_horizontal,
                                begin_angle=180 + angle_difference,
                                end_angle=360 - angle_difference,
                                base_color=horizontal_inner_color,
                                center=(center_x + circle_shift_horizontal, center_y),
                                spikes=right_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius_horizontal,
                                begin_angle=-angle_difference,
                                end_angle=180 + angle_difference,
                                base_color=horizontal_outer_color,
                                center=(center_x + circle_shift_horizontal, center_y),
                                mask=right_mask)

    # Left Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius_horizontal,
                                begin_angle=angle_difference,
                                end_angle=180 - angle_difference,
                                base_color=horizontal_inner_color,
                                center=(center_x - circle_shift_horizontal, center_y),
                                spikes=left_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius_horizontal,
                                begin_angle=180 - angle_difference,
                                end_angle=360 + angle_difference,
                                base_color=horizontal_outer_color,
                                center=(center_x - circle_shift_horizontal, center_y),
                                mask=left_mask)

    # Bottom Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius_vertical,
                                begin_angle=-angle_difference_2,
                                end_angle=angle_difference_2,
                                base_color=vertical_inner_color, center=(center_x, center_y + circle_shift_vertical),
                                spikes=bottom_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius_vertical,
                                begin_angle=angle_difference_2,
                                end_angle=360 - angle_difference_2,
                                base_color=vertical_outer_color, center=(center_x, center_y + circle_shift_vertical),
                                mask=bottom_mask)

    # Top Circle
    crystalograph.addLineToDraw(line_type=line_type, thickness=outer_line_thickness, radius=circle_radius_vertical,
                                begin_angle=180 - angle_difference_2, end_angle=180 + angle_difference_2,
                                base_color=vertical_inner_color, center=(center_x, center_y - circle_shift_vertical),
                                spikes=top_spikes)
    crystalograph.addLineToDraw(line_type=line_type, thickness=inner_line_thickness, radius=circle_radius_vertical,
                                begin_angle=-180 + angle_difference_2, end_angle=180 - angle_difference_2,
                                base_color=vertical_outer_color, center=(center_x, center_y - circle_shift_vertical),
                                mask=top_mask)

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
