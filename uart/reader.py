"""Implements the reader for the UART communication protocol."""
import logging
import threading
import time
from queue import Queue

import serial

from .command import Command, Message


class UartReader:
    """Reads data from the UART interface."""

    def __init__(self, port: str) -> None:
        self._logger = logging.getLogger('uart.reader')
        self._port = port
        self._commands: Queue = Queue()
        thread_reader = threading.Thread(target=self.read)
        thread_reader.start()

    def empty_queue(self) -> None:
        """Clears the queue."""
        while not self._commands.empty():
            self._commands.get()

    def is_empty(self) -> bool:
        """Returns true if the queue is empty."""
        return self._commands.empty()

    def get_from_queue(self) -> Message:
        """Returns a message from the queue."""
        return self._commands.get()

    def read(self):
        """Reads data received from UART."""
        ser = serial.Serial(self._port, 115200)
        while True:
            received_data = ser.read()
            time.sleep(0.03)
            data_left = ser.in_waiting
            received_data += ser.read(data_left)
            command = self._decode(received_data)
            if command is not None:
                self._commands.put(command)

    def _decode(self, received_data):
        """Decodes the message from the received data."""
        if len(received_data) != 23:
            self._logger.warning('Invalid length of data')
            return None

        preamble = received_data[:4]
        if preamble != b'AAAB':
            self._logger.debug('Invalid preamble')
            return None

        message_data = received_data[4:]
        message = Message.from_buffer_copy(message_data)
        command_type = Command(message.cmd)

        if command_type == Command.ACKNOWLEDGE:
            self._logger.debug('Acknowledged')
        elif command_type == Command.NOT_ACKNOWLEDGE:
            self._logger.debug('Not Acknowledged')
        elif command_type == Command.CRC_ERROR:
            self._logger.debug('CRC Error')
        else:
            self._logger.warning('Unhandled command: %s', command_type)

        return message
