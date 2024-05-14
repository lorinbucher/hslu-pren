"""Implements the writer for the UART communication protocol."""
import logging
import queue
import time
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event

import serial
from serial.serialutil import SerialException, SerialTimeoutException

from .command import Command, Message


class UartWriter:
    """Writes data to the UART interface."""

    def __init__(self, port: str, terminate: Event, ack_queue: Queue, write_queue: Queue) -> None:
        self._logger = logging.getLogger('uart.writer')
        self._port = port
        self._terminate = terminate
        self._ack_queue = ack_queue
        self._write_queue = write_queue
        self._process: Process | None = None
        self._ser: serial.Serial | None = None

    def start(self) -> None:
        """Starts the UART writer."""
        self._logger.info('Starting UART writer')
        self._process = Process(target=self._run)
        self._process.start()
        self._logger.info('UART writer started')

    def join(self) -> None:
        """Waits for the UART writer to complete."""
        if self._process is not None:
            self._logger.info('Waiting for UART writer to complete')
            self._process.join()
            self._logger.info('UART writer completed')

    def stop(self) -> None:
        """Stops the UART writer."""
        if self._process is not None:
            self._logger.info('Stopping UART writer')
            self._process.close()
            self._process = None
            self._logger.info('UART writer stopped')

    def alive(self) -> bool:
        """Returns true if the UART writer process is alive, false if not."""
        if self._process is not None:
            return self._process.is_alive()
        self._logger.info('UART writer process not alive')
        return False

    def _run(self) -> None:
        """Runs the UART writer process."""
        self._logger.info('UART writer process started')
        while not self._terminate.is_set():
            try:
                message = self._write_queue.get(timeout=2.0)
                if not isinstance(message, Message):
                    self._logger.warning('Invalid message type: %s', type(message))
                    continue
                self._write(message)
            except queue.Empty:
                continue

        if self._ser is not None and self._ser.is_open:
            self._ser.close()
        self._logger.info('UART writer process stopped')

    def _write(self, command) -> None:
        """Writes the command to the UART connection."""
        message = self._encode(command)
        acknowledged = False
        while not acknowledged and not self._terminate.is_set():
            try:
                self._logger.debug('Writing message: %s', message.hex(' '))
                if self._ser is None:
                    self._logger.info('Opening UART write connection')
                    self._ser = serial.Serial(self._port, 115200)
                if self._ser.is_open:
                    self._ser.write(message)

                ack_result = self._ack_queue.get(timeout=2.0)
                self._logger.debug('Received acknowledge result: %s', ack_result.cmd)
                if Command(ack_result.cmd) in (Command.ACKNOWLEDGE, Command.NOT_ACKNOWLEDGE):
                    acknowledged = True
            except (SerialException, SerialTimeoutException, ValueError) as error:
                self._logger.error('Failed to write message: %s', error)
                self._ser = None
                time.sleep(1)
            except queue.Empty:
                self._logger.warning('No acknowledge result received, retrying')

    @staticmethod
    def _encode(command: Message) -> bytes:
        """Encodes the command with the preamble."""
        return b'AAAB' + command
