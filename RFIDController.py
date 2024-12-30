from typing import List, Callable

import serial
import logging
import threading
import time


class RFIDController:
    def __init__(self,
                 on_card_detected_callback: Callable[[str], None],
                 on_card_lost_callback: Callable[[str], None],
                 traits_detected_callback: Callable[[List[str]], None],
                 baud_rate = 115200):
        # Handle listening to serial.
        self._serial_send_thread = threading.Thread(target=self._handleSerialSend, daemon=True)
        self._serial_listen_thread = threading.Thread(target=self._handleSerialListen, daemon=True)

        self._baud_rate = baud_rate
        self._serial = None
        self._on_card_detected_callback = on_card_detected_callback
        self._on_card_lost_callback = on_card_lost_callback
        self._traits_detected_callback = traits_detected_callback
        self._detected_card = None
        self._recreate_serial_timer = None
        self._serial_recreate_time = 5
        self._request_trait_info = True # Should we re-request trait info?

    def getDetectedCard(self):
        return self._detected_card

    def start(self) -> None:
        # TODO: Should probably handle starting it multiple times?
        self._createSerial()

    def stop(self):
        self._serial = None
        if self._recreate_serial_timer:
            self._recreate_serial_timer.cancel()

    def _recreateSerial(self):
        logging.warning("Previously working serial has stopped working, try to re-create!")
        self._serial = None
        # Try to re-create it after a few seconds
        self._recreate_serial_timer = threading.Timer(self._serial_recreate_time, self._createSerial)
        self._recreate_serial_timer.start()

    def _sendCommand(self, command=""):
        # TODO: add command validity checking.
        if self._serial:
            self._serial.write(b"\n")
            command += "\n"
            self._serial.write(command.encode('utf-8'))
        else:
            logging.error("Unable to write command %s without serial connection" % command)

    def _handleSerialSend(self):
        logging.info("Starting serial send thread")

        while self._serial is not None:
            try:
                if self._request_trait_info:
                    self._sendCommand("READ ALL")
                    self._request_trait_info = False
                # It no like spinlocking :(
                time.sleep(0.1)
            except serial.SerialException:
                self._recreateSerial()
            except Exception as e:
                logging.error(f"Serial broke with exception of type {type(e)}: {e}")
                time.sleep(0.1)  # Prevent error spam.

    def _validateCardTraits(self, arguments: List[str]) -> bool:
        logging.info(f"Checking reader response {arguments}")
        if arguments[0] != "RAW" and arguments[0] != "REFINED":
            logging.warning(f"INVALID TYPE: {arguments[1]}")
            return False

        # If we get "EMPTY" it means that they just got a weird tag with no traits
        # on it. We need to fix that
        if arguments[0] == "EMPTY":
            logging.warning(f"EMPTY TAG")
            return False

        # We send traits back in all caps, which serves as a rudimentary check
        # To see if the reading is correct
        if any(arg != arg.upper() for arg in arguments[1:]):
            logging.warning("Invalid response")
            return False
        return True

    def _handleSerialListen(self):
        logging.info("Starting serial listen thread")
        while self._serial is not None:
            try:
                line = self._serial.readline()
                line = line.rstrip()  # Strip newlines
                line = line.decode("utf-8")
                if line.startswith("Tag found:"):
                    response = line.replace("Tag found: ", "")
                    arguments = response.split(" ")
                    card_id = arguments[0]
                    self._detected_card = card_id
                    self._on_card_detected_callback(card_id)
                    if not self._validateCardTraits(arguments[1:]):
                        # TODO: Send read all command!
                        self._request_trait_info = True
                    else:
                        self._traits_detected_callback(arguments[1:])
                elif line.startswith("Tag lost:"):
                    card_id = line.replace("Tag lost: ", "")
                    self._detected_card = None
                    self._on_card_lost_callback(card_id)
                elif line.startswith("Traits: "):
                    response = line.replace("Traits: ", "")
                    arguments = response.split(" ")
                    if self._validateCardTraits(arguments):
                        self._traits_detected_callback(arguments)
                    else:
                        logging.warning("READ ALL FAILED :(")

            except serial.SerialException:
                self._recreateSerial()
            except Exception as e:
                logging.error(f"Serial broke with exception of type {type(e)}: {e}")
                time.sleep(0.1)  # Prevent error spam.

    def _startSerialThread(self) -> None:
        self._serial_listen_thread.start()
        self._serial_send_thread.start()

    def _createSerial(self) -> None:
        logging.info("Attempting to create serial")
        try:
            self._serial_listen_thread.join()  # Ensure that previous thread has closed
            self._serial_listen_thread = threading.Thread(target=self._handleSerialListen, daemon=True)
        except RuntimeError:
            # If the thread hasn't started before it will cause a runtime. Ignore that.
            pass

        try:
            self._serial_send_thread.join()
            self._serial_send_thread = threading.Thread(target=self._handleSerialSend(), daemon=True)
        except RuntimeError:
            pass

        for i in range(0, 10):
            try:
                port = f"/dev/ttyUSB{i}"
                self._serial = serial.Serial(port, self._baud_rate, timeout=3)
                logging.info(f"Connected with serial {port}")
                break
            except Exception:
                pass
            try:
                port = f"/dev/ttyACM{i}"
                self._serial = serial.Serial(port, self._baud_rate, timeout=3)
                logging.info(f"Connected with serial {port}")
                break
            except Exception:
                pass

        if self._serial is not None:
            # Call later
            threading.Timer(2, self._startSerialThread).start()
        else:
            logging.warning("Unable to create serial. Attempting again in a few seconds.")
            # Check again after a bit of time has passed
            self._recreate_serial_timer = threading.Timer(self._serial_recreate_time, self._createSerial)
            self._recreate_serial_timer.start()


