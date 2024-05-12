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
        self._terminate = Event()
        self._ack_queue: Queue = Queue()
        self._reader = UartReader(app_config.serial_read, self._terminate, self._ack_queue, read_queue)
        self._writer = UartWriter(app_config.serial_write, self._terminate, self._ack_queue, write_queue)

    def start(self) -> None:
        """Starts the UART reader and writer tasks."""
        self._logger.info('Starting UART tasks')
        self._terminate.clear()
        self._reader.start()
        self._writer.start()
        self._logger.info('UART tasks started')

    def join(self) -> None:
        """Waits for UART reader and writer tasks to complete."""
        self._logger.info('Waiting for UART tasks to complete')
        self._reader.join()
        self._writer.join()
        self._logger.info('UART tasks completed')

    def stop(self) -> None:
        """Stops the UART reader and writer tasks."""
        self._logger.info('Stopping UART tasks')
        self._reader.stop()
        self._writer.stop()
        self._logger.info('UART tasks stopped')

    def terminate_signal(self) -> None:
        """Sends the terminate event to the UART reader and writer tasks."""
        self._terminate.set()
