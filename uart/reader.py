"""Implements the reader for the UART communication protocol."""
import logging
import time
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event

import serial
from serial.serialutil import SerialException, SerialTimeoutException

from .command import Command, Message


class UartReader:
    """Reads data from the UART interface."""

    def __init__(self, port: str, terminate: Event, ack_queue: Queue, read_queue: Queue) -> None:
        self._logger = logging.getLogger('uart.reader')
        self._port = port
        self._terminate = terminate
        self._ack_queue = ack_queue
        self._read_queue = read_queue
        self._process: Process | None = None
        self._ser: serial.Serial | None = None

    def start(self) -> None:
        """Starts the UART reader."""
        self._logger.info('Starting UART reader')
        self._process = Process(target=self._run)
        self._process.start()
        self._logger.info('UART reader started')

    def join(self) -> None:
        """Waits for the UART reader to complete."""
        if self._process is not None:
            self._logger.info('Waiting for UART reader to complete')
            self._process.join()
            self._logger.info('UART reader completed')

    def stop(self) -> None:
        """Stops the UART reader."""
        if self._process is not None:
            self._logger.info('Stopping UART reader')
            self._process.close()
            self._process = None
            self._logger.info('UART reader stopped')

    def alive(self) -> bool:
        """Returns true if the UART reader process is alive, false if not."""
        if self._process is not None:
            return self._process.is_alive()
        self._logger.info('UART reader process not alive')
        return False

    def _run(self) -> None:
        """Runs the UART reader process."""
        self._logger.info('UART reader process started')
        data = b''
        while not self._terminate.is_set():
            data += self._read()
            preamble_pos = data.find(b'AAAB')
            if preamble_pos < 0:
                data = b''
                continue

            data = data[preamble_pos:]
            if len(data) >= 23:
                if self._decode(data[:23]):
                    data = data[23:]
                else:
                    data = data[4:]

        if self._ser is not None and self._ser.is_open:
            self._ser.close()
        self._logger.info('UART reader process stopped')

    def _read(self) -> bytes:
        """Reads data received from the UART connection."""
        try:
            if self._ser is None:
                self._logger.info('Opening UART read connection')
                self._ser = serial.Serial(self._port, 115200, timeout=2.0)
            if self._ser.is_open:
                return self._ser.read(23)
        except (SerialException, SerialTimeoutException, ValueError) as error:
            self._logger.error('Failed to read message: %s', error)
            self._ser = None
            time.sleep(1)
        return bytes()

    def _decode(self, data: bytes) -> bool:
        """Decodes the message from the received data."""
        try:
            message_data = data[4:]
            message = Message.from_buffer_copy(message_data)
            command_type = Command(message.cmd)

            self._logger.debug('Received command: %s', command_type)
            if command_type in (Command.ACKNOWLEDGE, Command.NOT_ACKNOWLEDGE, Command.CRC_ERROR):
                self._ack_queue.put(message)
            elif command_type == Command.SEND_STATE:
                self._read_queue.put(message)
            else:
                self._logger.info('Unhandled command received: %s', command_type)
            return True
        except ValueError as error:
            self._logger.warning('Invalid message received: %s', error)
        return False
