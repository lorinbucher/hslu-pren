"""Implements the UART communication protocol."""
import logging
from multiprocessing import Event, Queue

from shared.data import AppConfiguration
from .reader import UartReader
from .writer import UartWriter


class UartCommunicator:
    """Manages the communication with the electronics controller using the UART communication protocol."""

    def __init__(self, app_config: AppConfiguration, read_queue: Queue, write_queue: Queue):
        self._logger = logging.getLogger('uart.communicator')
        self._halt_reader = Event()
        self._halt_writer = Event()
        self._ack_queue: Queue = Queue()
        self._reader = UartReader(app_config.serial_read, self._halt_reader, self._ack_queue, read_queue)
        self._writer = UartWriter(app_config.serial_write, self._halt_writer, self._ack_queue, write_queue)

    def start(self, reader: bool = True, writer: bool = True) -> None:
        """Starts the UART reader and/or writer tasks."""
        if reader:
            self._halt_reader.clear()
            self._reader.start()
        if writer:
            self._halt_writer.clear()
            self._writer.start()

    def join(self, reader: bool = True, writer: bool = True) -> None:
        """Waits for UART reader and/or writer tasks to complete."""
        if reader:
            self._reader.join()
        if writer:
            self._writer.join()

    def stop(self, reader: bool = True, writer: bool = True) -> None:
        """Stops the UART reader and/or writer tasks."""
        if reader:
            self._reader.stop()
        if writer:
            self._writer.stop()

    def halt(self, reader: bool = True, writer: bool = True) -> None:
        """Sends the halt event to the UART reader and/or writer tasks."""
        if reader:
            self._halt_reader.set()
        if writer:
            self._halt_writer.set()

    def alive(self, reader: bool = True, writer: bool = True) -> bool:
        """Checks if the UART reader and/or writer taskss are alive."""
        if reader and writer:
            return self._reader.alive() and self._writer.alive()
        elif reader:
            return self._reader.alive()
        elif writer:
            return self._writer.alive()
        return False
