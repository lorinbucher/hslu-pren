"""Helper classes to simulate the electronics controller used for development."""
import sys

import serial

from uart.command import ButtonState, Command, DataUnion, LiftState, Message, WerniState
from uart.commandbuilder import CommandBuilder


class ElectronicsSimulator:
    """Simulates the electronics controller."""

    def __init__(self, read_port: str, write_port: str) -> None:
        self._read_port = read_port
        self._write_port = write_port

    def run(self) -> None:
        """Simulates responses from the electronics controller."""
        while True:
            self._read()
            message: Message | bytes = b''
            command = int(input('1 ack, 2 nack, 3 crc, 4 start, 5 finished, 6 state, 9 disturb: '))
            if command == 1:
                message = CommandBuilder.other_command(Command.ACKNOWLEDGE)
            elif command == 2:
                message = CommandBuilder.other_command(Command.NOT_ACKNOWLEDGE)
            elif command == 3:
                message = CommandBuilder.other_command(Command.CRC_ERROR)
            elif command == 4:
                message = self._send_io_state()
            elif command == 5:
                message = self._exec_finished()
            elif command == 6:
                message = self._send_state()
            elif command == 9:
                data = input('data: ')
                message = data.encode('utf-8')
            else:
                sys.exit(0)

            self._write(message)

    @staticmethod
    def _send_state() -> Message:
        """Creates the message for the send state command."""
        data = DataUnion()
        data.send_state.energy = 10.0
        data.send_state.lift_state = LiftState.LIFT_DOWN.value
        data.send_state.werni_state = WerniState.BUILDING.value
        return CommandBuilder.other_command(Command.SEND_STATE, data)

    @staticmethod
    def _send_io_state() -> Message:
        """Creates the message for the send IO state command."""
        data = DataUnion()
        data.send_io_state.btn_start = ButtonState.LONG_CLICKED.value
        data.send_io_state.btn_stop = ButtonState.RELEASED.value
        return CommandBuilder.other_command(Command.SEND_IO_STATE, data)

    @staticmethod
    def _exec_finished() -> Message:
        """Creates the message for the execution finished command."""
        data = DataUnion()
        data.exec_finished.cmd = Command.MOVE_LIFT.value
        return CommandBuilder.other_command(Command.EXECUTION_FINISHED, data)

    def _read(self) -> None:
        """Reads data from the UART connection."""
        ser = serial.Serial(self._read_port, 115200, timeout=2.0)
        data = ser.read(23)
        if not data:
            return

        if data[:4] != b'AAAB':
            print('Invalid preamble')
            return

        message_data = data[4:]
        message = Message.from_buffer_copy(message_data)
        print(Command(message.cmd))

    def _write(self, command: Message | bytes) -> None:
        """Writes the command to the UART connection."""
        ser = serial.Serial(self._write_port, 115200)
        if isinstance(command, Message):
            ser.write(b'AAAB' + command)
        else:
            ser.write(command)


if __name__ == '__main__':
    serial_read = input('Select UART read port: ')
    serial_write = input('Select UART write port: ')

    simulator = ElectronicsSimulator(serial_read, serial_write)
    simulator.run()
