"""Implements the writer for the UART communication protocol."""
import logging

import serial
from serial.serialutil import SerialException, SerialTimeoutException

from .command import Message


class UartWriter:
    """Writes data to the UART interface."""

    def __init__(self, port: str) -> None:
        self._logger = logging.getLogger('uart.writer')
        self._port = port
        self._ser: serial.Serial | None = None

        self._open_connection()

    def write(self, command) -> int | None:
        """Writes the command to the UART connection."""
        if not self._open_connection():
            self._logger.warning('UART connection is not opened')
            return None

        message = self._encode(command)
        try:
            self._logger.debug('Writing message: %s', message)
            return self._ser.write(message) if self._ser is not None else None
        except (SerialException, SerialTimeoutException) as error:
            self._logger.error('Failed to write message: %s', error)
            self._ser = None
        return 0

    def _open_connection(self) -> bool:
        """Opens the UART connection."""
        if self._ser is not None and self._ser.is_open:
            return True

        self._logger.info('Opening UART write connection')
        try:
            self._ser = serial.Serial(self._port, 115200)
            self._logger.info('UART write connection opened')
            return True
        except (SerialException, ValueError) as error:
            self._logger.error('Failed to open UART write connection: %s', error)
        return False

    @staticmethod
    def _encode(command: Message) -> bytes:
        """Encodes the command with the preamble."""
        return b'AAAB' + command
