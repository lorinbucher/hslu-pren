"""Implements the UART communication protocol."""
import logging
from time import sleep

from shared.data import AppConfiguration

from .command import Command, Message
from .reader import UartReader
from .writer import UartWriter


class UartCommunicator:
    """Communicates with the electronics controller using the UART communication protocol."""

    def __init__(self, app_config: AppConfiguration):
        self._logger = logging.getLogger('uart.communicator')
        self._reader = UartReader(app_config.serial_read)
        self._writer = UartWriter(app_config.serial_write)

    def read_acknowledge(self) -> bool:
        """Checks if the command has been acknowledged."""
        while not self._reader.is_empty():
            command = self._reader.get_from_queue()
            action = Command(command.cmd)
            if action == Command.ACKNOWLEDGE or action == Command.NOT_ACKNOWLEDGE:
                return True
        return False

    def write_uart(self, cmd: Message) -> None:
        """Writes a command to the UART interface."""
        self._reader.empty_queue()
        while not self.read_acknowledge():
            self._writer.write(cmd)
            sleep(1.0)
