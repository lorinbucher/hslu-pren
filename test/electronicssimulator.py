"""Helper classes to simulate the electronics controller used for development."""
import logging
import sys

from uart.command import Command
from uart.commandbuilder import CommandBuilder
from uart.reader import UartReader
from uart.writer import UartWriter


class ElectronicsSimulator:
    """Simulates the electronics controller."""

    def __init__(self, read: str, write: str) -> None:
        self._reader = UartReader(read)
        self._writer = UartWriter(write)

    def acknowledge(self) -> None:
        """Sends an acknowledged message."""
        command = CommandBuilder.other_command(Command.ACKNOWLEDGE)
        self._writer.write(command)

    def not_acknowledge(self) -> None:
        """Sends a not acknowledged message."""
        command = CommandBuilder.other_command(Command.NOT_ACKNOWLEDGE)
        self._writer.write(command)

    def checksum_error(self) -> None:
        """Sends a checksum error message."""
        command = CommandBuilder.other_command(Command.CRC_ERROR)
        self._writer.write(command)

    def disturb(self) -> None:
        """Sends data to disturb."""
        self._writer.write(b'\x06\x01\x00\x00\x00')

    def simulate(self) -> None:
        """Simulates responses from the electronics controller."""
        while True:
            command = int(input('1 ack, 2 nack, 3 crc: '))
            if command == 1:
                self.acknowledge()
            elif command == 2:
                self.not_acknowledge()
            elif command == 3:
                self.checksum_error()
            else:
                sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serial_read = input('Select UART read port: ')
    serial_write = input('Select UART write port: ')
    sim = ElectronicsSimulator(serial_read, serial_write)
    sim.simulate()
