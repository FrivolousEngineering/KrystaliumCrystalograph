import argparse
import contextlib
import random
import requests
import logging
import sys


from Fader import Fader
from GlitchHandler import GlitchHandler
from RFIDController import RFIDController
from sql_app.schemas import Action, Target

# This suppresses the `Hello from pygame` message.
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

    crystalograph.drawHorizontalPatterns("green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                                         circle_shift, list(Action)[action_index], list(Target)[target_index])
    crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift, list(Action)[action_index], list(Target)[target_index])


def addRandomLinesToCrystalograph(crystalograph):
    circle_shift = 125
    circle_radius = 200
    line_thickness = 3
    outer_line_thickness = line_thickness
    inner_line_thickness = line_thickness + 2
    crystalograph.drawHorizontalPatterns("green", "blue", inner_line_thickness, outer_line_thickness, circle_radius,
                                         circle_shift, "Expanding", "Flesh")
    crystalograph.drawVerticalPatterns("green_2", "blue_2", inner_line_thickness, outer_line_thickness, circle_radius,
                                       circle_shift, "Heating", "Krystal")


class PygameWrapper:
    def __init__(self, fullscreen: bool = True):
        pygame.init()
        self._screen_width = 1280
        self._screen_height = 720
        if fullscreen:
            self._screen = pygame.display.set_mode((self._screen_width, self._screen_height), pygame.FULLSCREEN)
        else:
            self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        self._clock = pygame.time.Clock()
        self._running = True
        self._crystalograph = Crystalograph.Crystalograph()
        self._glitch_handler = GlitchHandler()
        self._rfid_controller = RFIDController(self._onCardDetected, self._onCardLost)
        self._rfid_controller.start()

        self._crystalograph.createEmptyImage((self._screen_width, self._screen_height))

        self._base_server_url: str = "http://127.0.0.1:8000"

        self._crystalograph.setup()
        self._fader = Fader()
        self._screen_shake = 0
        self._current_action_index = 0
        self._current_target_index = 0
        self._setupLogging()

        self._new_sample_to_draw = None

    @staticmethod
    def _setupLogging() -> None:
        root = logging.getLogger()

        # Kick out the default handler
        root.removeHandler(root.handlers[0])

        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    def _onCardLost(self, rfid_id):
        logging.info(f"Card lost {rfid_id}")

        # We only fade out, as we don't want the pattern to disapear right away

        self._fader.fadeOut()

    def _onCardDetected(self, rfid_id):
        logging.info(f"Card detected {rfid_id}")
        try:
            r = requests.get(f"{self._base_server_url}/samples/{rfid_id}")
        except requests.exceptions.ConnectionError:
            logging.error("Failed to connect to the server")
            return

        if r.status_code == 200:
            self._crystalograph.clearLinesToDraw()

            data = r.json()
            # Set the data for next update draw loop to be updated. Since this is called outside of the main thread,
            # we do it like this to prevent threading issues.
            self._new_sample_to_draw = data
        elif r.status_code == 404:
            # It's not a raw sample, find out if it's a refined one
            try:
                r = requests.get(f"{self._base_server_url}/refined/{rfid_id}")
            except requests.exceptions.ConnectionError:
                logging.error("Failed to connect to the server")
                return
            if r.status_code == 200:
                self._crystalograph.clearLinesToDraw()

                data = r.json()
                # Set the data for next update draw loop to be updated. Since this is called outside of the main thread,
                # we do it like this to prevent threading issues.
                self._new_sample_to_draw = data
            else:

                logging.warning(f"Failed to get remote info for {rfid_id}, got status code {r.status_code}")
        else:
            logging.warning(f"Failed to get remote info for {rfid_id}, got status code {r.status_code}")

    def run(self):
        logging.info("Display has started")
        pygame.mouse.set_visible(False)
        while self._running:
            if self._new_sample_to_draw is not None and not self._fader.isFading():
                # Only re-draw if we have a new sample, and we are done with any fade operation!
                circle_shift = 125
                circle_radius = 200
                line_thickness = 3
                outer_line_thickness = line_thickness
                inner_line_thickness = line_thickness + 2

                # If depleted is not set, it can be a refined sample
                is_depleted = self._new_sample_to_draw.get("depleted", False)
                inner_color = "green"
                outer_color = "blue"

                if is_depleted:
                    # Sample is depleted, draw it with much darker colors
                    inner_color = f"dark_{inner_color}"
                    outer_color = f"dark_{outer_color}"

                if "vulgarity" in self._new_sample_to_draw:  # It's a raw sample
                    horizontal_action = self._new_sample_to_draw.get("positive_action")
                    horizontal_target = self._new_sample_to_draw.get("positive_target")

                    vertical_action = self._new_sample_to_draw.get("negative_action")
                    vertical_target = self._new_sample_to_draw.get("negative_target")
                else:  # It's a refined sample
                    horizontal_action = self._new_sample_to_draw.get("primary_action")
                    horizontal_target = self._new_sample_to_draw.get("primary_target")

                    vertical_action = self._new_sample_to_draw.get("secondary_action")
                    vertical_target = self._new_sample_to_draw.get("secondary_target")

                self._crystalograph.drawHorizontalPatterns(inner_color, outer_color, inner_line_thickness,
                                                           outer_line_thickness, circle_radius, circle_shift,
                                                           horizontal_action, horizontal_target)
                self._crystalograph.drawVerticalPatterns(f"{inner_color}_2", f"{outer_color}_2", inner_line_thickness,
                                                         outer_line_thickness, circle_radius,
                                                         circle_shift, vertical_action, vertical_target)

                self._crystalograph.setup()
                # We have something to show, fade in the new pattern!
                self._fader.fadeIn()

                self._new_sample_to_draw = None

            image = self._crystalograph.draw()
            self._screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    # Toggle fullscreen (DEBUG)
                    pygame.display.toggle_fullscreen()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    # Force fadein (DEBUG)
                    self._fader.fadeIn()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    # Force fadeout (DEBUG)
                    self._fader.fadeOut()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                    # Shake the screen (DEBUG)
                    self._screen_shake += 40
                if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    # Show random (DEBUG)
                    self._crystalograph.clearLinesToDraw()
                    addRandomLinesToCrystalograph(self._crystalograph)
                    self._crystalograph.setup()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    # Cycle to next action (DEBUG)
                    self._crystalograph.clearLinesToDraw()
                    self._current_action_index += 1
                    if self._current_action_index > 16:
                        self._current_action_index = 0
                    addLinesToCrystalopgrah(self._crystalograph, target_index=self._current_target_index,
                                            action_index=self._current_action_index)
                    self._crystalograph.setup()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    # Cycle to next target (DEBUG)
                    self._crystalograph.clearLinesToDraw()
                    self._current_target_index += 1
                    if self._current_target_index > 9:
                        self._current_target_index = 0
                    addLinesToCrystalopgrah(self._crystalograph, target_index=self._current_target_index,
                                            action_index=self._current_action_index)
                    self._crystalograph.setup()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    # Save current image shown on screen (DEBUG)
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

            # This is optionally sliiightly faster.
            #pygame.surfarray.blit_array(self._screen, np.fliplr(np.rot90(image, k=-1)))

            self._fader.draw(self._screen)
            self._glitch_handler.draw(self._screen)

            pygame.display.flip()
            self._crystalograph.update()
            self._clock.tick()

        self._rfid_controller.stop()
        quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--windowed", action="store_true")

    args = parser.parse_args()
    wrapper = PygameWrapper(fullscreen = not args.windowed)

    wrapper.run()
