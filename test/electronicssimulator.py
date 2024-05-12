"""Helper classes to simulate the electronics controller used for development."""
import sys

import serial

from uart.command import Command, Message
from uart.commandbuilder import CommandBuilder


class ElectronicsSimulator:
    """Simulates the electronics controller."""

    def __init__(self, read_port: str, write_port: str) -> None:
        self._read_port = read_port
        self._write_port = write_port

    def acknowledge(self) -> None:
        """Sends an acknowledged message."""
        command = CommandBuilder.other_command(Command.ACKNOWLEDGE)
        self._write(command)

    def not_acknowledge(self) -> None:
        """Sends a not acknowledged message."""
        command = CommandBuilder.other_command(Command.NOT_ACKNOWLEDGE)
        self._write(command)

    def checksum_error(self) -> None:
        """Sends a checksum error message."""
        command = CommandBuilder.other_command(Command.CRC_ERROR)
        self._write(command)

    def get_state(self) -> None:
        """Sends a checksum error message."""
        command = CommandBuilder.other_command(Command.GET_STATE)
        self._write(command)

    def send_state(self) -> None:
        """Sends a checksum error message."""
        command = CommandBuilder.other_command(Command.SEND_STATE)
        self._write(command)

    def simulate(self) -> None:
        """Simulates responses from the electronics controller."""
        while True:
            self._read()
            command = int(input('1 ack, 2 nack, 3 crc, 7 get state, 8 send state: '))
            if command == 1:
                self.acknowledge()
            elif command == 2:
                self.not_acknowledge()
            elif command == 3:
                self.checksum_error()
            elif command == 7:
                self.get_state()
            elif command == 8:
                self.send_state()
            else:
                sys.exit(0)

    def _read(self) -> None:
        """Reads data from the UART connection."""
        ser = serial.Serial(self._read_port, 115200, timeout=5.0)
        data = ser.read(23)
        if not data:
            return

        if data[:4] != b'AAAB':
            print('Invalid preamble')
            return

        message_data = data[4:]
        message = Message.from_buffer_copy(message_data)
        print(Command(message.cmd))

    def _write(self, command) -> None:
        """Writes the command to the UART connection."""
        ser = serial.Serial(self._write_port, 115200)
        ser.write(b'AAAB' + command)


if __name__ == '__main__':
    serial_read = input('Select UART read port: ')
    serial_write = input('Select UART write port: ')

    sim = ElectronicsSimulator(serial_read, serial_write)
    sim.simulate()
