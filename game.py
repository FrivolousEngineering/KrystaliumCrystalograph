import contextlib
import random
import requests

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
                                         circle_shift, "Expanding", "Flesh")
    print("Negative:")
    crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift, "Heating", "Krystal")


class PygameWrapper:
    def __init__(self):
        pygame.init()
        self._screen_width = 1280
        self._screen_height = 720
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        self._clock = pygame.time.Clock()
        self._running = True
        self._crystalograph = Crystalograph.Crystalograph()
        self._glitch_handler = GlitchHandler()
        self._rfid_controller = RFIDController(self._onCardDetected, self._onCardLost)
        self._rfid_controller.start()

        self._crystalograph.createEmptyImage((self._screen_width, self._screen_height))

        addRandomLinesToCrystalograph(self._crystalograph)
        #self._crystalograph.addLineToDraw("double_line", "green", 50, 2, (int(self._screen_width/2), int(self._screen_height/2)), 0, 360, mask = [(90, 10), (270, 10)])

        self._crystalograph.setup()
        self._fader = Fader()
        self._screen_shake = 0
        self._current_action_index = 0
        self._current_target_index = 0


    def _onCardLost(self, rfid_id):
        print("Card lost", rfid_id)

    def _onCardDetected(self, rfid_id):

        print("Card Detected", rfid_id)
        r = requests.get(f"http://127.0.0.1:8000/samples/{rfid_id}")

        if r.status_code == 200:
            self._crystalograph.clearLinesToDraw()

            data = r.json()

            circle_shift = 125
            circle_radius = 200
            line_thickness = 3
            outer_line_thickness = line_thickness
            inner_line_thickness = line_thickness + 2

            self._crystalograph.drawHorizontalPatterns("green", "blue", inner_line_thickness, outer_line_thickness,
                                                 circle_radius,
                                                 circle_shift, data["positive_action"], data["positive_target"])
            self._crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift, data["negative_action"], data["negative_target"])

            self._crystalograph.setup()
        print(r.json())

    def run(self):
        while self._running:

            image = self._crystalograph.draw()
            self._screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    self._fader.fadeIn()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    self._fader.fadeOut()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                    self._screen_shake += 40
                if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    self._crystalograph.clearLinesToDraw()
                    addRandomLinesToCrystalograph(self._crystalograph)
                    self._crystalograph.setup()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    print("Increasing action")
                    self._crystalograph.clearLinesToDraw()
                    self._current_action_index += 1
                    if self._current_action_index > 16:
                        self._current_action_index = 0
                    addLinesToCrystalopgrah(self._crystalograph, target_index=self._current_target_index,
                                            action_index=self._current_action_index)
                    self._crystalograph.setup()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    print("Increasing action")
                    self._crystalograph.clearLinesToDraw()
                    self._current_target_index += 1
                    if self._current_target_index > 9:
                        self._current_target_index = 0
                    addLinesToCrystalopgrah(self._crystalograph, target_index=self._current_target_index,
                                            action_index=self._current_action_index)
                    self._crystalograph.setup()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    print("Saving")
                    import cv2

                    cv2.imwrite(
                        f"action_{list(Action)[self._current_action_index - 1].value}_target_{list(Target)[self._current_target_index].value}.png",
                        image)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    self._glitch_handler.glitch()

            if self._screen_shake:
                screen_displacement_x = random.random() * 4 - 2
                screen_displacement_y = random.random() * 4 - 2
                self._screen_shake -= 1
            else:
                screen_displacement_x = 0
                screen_displacement_y = 0

            self._fader.update()
            self._glitch_handler.update()

            # This is where we insert the numpy array.
            # Because pygame and numpy use different coordinate systems,
            # the numpy image has to be flipped and rotated, before being blit.
            img = pygame.surfarray.make_surface(np.fliplr(np.rot90(image, k=-1)))
            self._screen.blit(img, (screen_displacement_x, screen_displacement_y))

            self._fader.draw(self._screen)
            self._glitch_handler.draw(self._screen)

            pygame.display.flip()
            self._crystalograph.update()
            self._clock.tick()
            print(self._clock.get_fps())
        quit()



if __name__ == '__main__':
    wrapper = PygameWrapper()

    wrapper.run()
