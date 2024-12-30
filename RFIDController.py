import serial
import logging
import threading
import time


class RFIDController:
    def __init__(self, on_card_detected_callback, on_card_lost_callback, baud_rate = 9600):
        # Handle listening to serial.
        self._serial_listen_thread = threading.Thread(target=self._handleSerialListen, daemon=True)
        self._baud_rate = baud_rate
        self._serial = None
        self._on_card_detected_callback = on_card_detected_callback
        self._on_card_lost_callback = on_card_lost_callback
        self._detected_card = None
        self._recreate_serial_timer = None
        self._serial_recreate_time = 5

    def getDetectedCard(self):
        return self._detected_card

    def start(self) -> None:
        # TODO: Should probably handle starting it multiple times?
        self._createSerial()

    def stop(self):
        self._serial = None
        if self._recreate_serial_timer:
            self._recreate_serial_timer.cancel()

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
                elif line.startswith("Tag lost:"):
                    card_id = line.replace("Tag lost: ", "")
                    self._detected_card = None
                    self._on_card_lost_callback(card_id)
            except serial.SerialException:
                logging.warning("Previously working serial has stopped working, try to re-create!")
                self._serial = None
                # Try to re-create it after a few seconds
                self._recreate_serial_timer = threading.Timer(self._serial_recreate_time, self._createSerial)
                self._recreate_serial_timer.start()
            except Exception as e:
                logging.error(f"Serial broke with exception of type {type(e)}: {e}")
                time.sleep(0.1)  # Prevent error spam.

    def _startSerialThread(self) -> None:
        self._serial_listen_thread.start()

    def _createSerial(self) -> None:
        logging.info("Attempting to create serial")
        try:
            self._serial_listen_thread.join()  # Ensure that previous thread has closed
            self._serial_listen_thread = threading.Thread(target=self._handleSerialListen, daemon=True)
        except RuntimeError:
            # If the thread hasn't started before it will cause a runtime. Ignore that.
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


