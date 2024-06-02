"""Helper classes to simulate the electronics controller used for development."""
import concurrent.futures
import queue
import time
from queue import Queue
from threading import Event

import serial

from uart.command import ButtonState, Command, DataUnion, LiftState, Message, WerniState
from uart.commandbuilder import CommandBuilder


class ElectronicsSimulator:
    """Simulates the electronics controller."""

    def __init__(self, read_port: str, write_port: str) -> None:
        self._read_port = read_port
        self._write_port = write_port
        self._halt_event = Event()
        self._pause_event = Event()
        self._message_queue: Queue = Queue()

    def control_simulator(self) -> None:
        """Controls the simulator."""
        while not self._halt_event.is_set():
            action = int(input('Action (1 start, 2 stop, 3 exit): '))
            if action == 1:
                self._write(self._send_io_state(start_state=ButtonState.LONG_CLICKED, stop_state=ButtonState.RELEASED))
            elif action == 2:
                self._write(self._send_io_state(start_state=ButtonState.RELEASED, stop_state=ButtonState.SHORT_CLICKED))
            elif action == 3:
                self._halt_event.set()

    def simulate_reader(self) -> None:
        """Simulates the uart reader."""
        last_id = 0
        while not self._halt_event.is_set():
            message = self._read()
            if not message:
                continue

            if CommandBuilder.calculate_checksum(message) != message.checksum:
                print('CRC error')
                self._write(CommandBuilder.other_command(Command.CRC_ERROR))
                continue

            if last_id == message.id:
                print('NACK')
                self._write(CommandBuilder.other_command(Command.NOT_ACKNOWLEDGE))
                continue

            last_id = message.id
            command = Command(message.cmd)
            print(f'Received command: {command}')
            self._write(CommandBuilder.other_command(Command.ACKNOWLEDGE))

            if command == Command.GET_STATE:
                print('Sending state: LIFT_DOWN')
                self._write(self._send_state(LiftState.LIFT_DOWN))
            elif command == Command.PAUSE_BUILD:
                print('Pausing build')
                self._pause_event.set()
            elif command == Command.RESUME_BUILD:
                print('Resuming build')
                self._pause_event.clear()
            else:
                self._message_queue.put(message)

    def simulate_execution(self) -> None:
        """Simulates the command execution."""
        while not self._halt_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue

            try:
                message = self._message_queue.get(timeout=2.0)
            except queue.Empty:
                continue

            command = Command(message.cmd)
            print(f'Execute command: {command}')
            if command == Command.MOVE_LIFT:
                time.sleep(2)
            elif command in (Command.ROTATE_GRID, Command.PLACE_CUBES, Command.PRIME_MAGAZINE):
                time.sleep(0.25)
            self._write(self._exec_finished(command))

    @staticmethod
    def _send_state(lift_state: LiftState) -> Message:
        """Creates the message for the send state command."""
        data = DataUnion()
        data.send_state.energy = 10.0
        data.send_state.lift_state = lift_state.value
        data.send_state.werni_state = WerniState.BUILDING.value
        return CommandBuilder.other_command(Command.SEND_STATE, data)

    @staticmethod
    def _send_io_state(start_state: ButtonState, stop_state: ButtonState) -> Message:
        """Creates the message for the send IO state command."""
        data = DataUnion()
        data.send_io_state.btn_start = start_state.value
        data.send_io_state.btn_stop = stop_state.value
        return CommandBuilder.other_command(Command.SEND_IO_STATE, data)

    @staticmethod
    def _exec_finished(cmd: Command) -> Message:
        """Creates the message for the execution finished command."""
        data = DataUnion()
        data.exec_finished.cmd = cmd.value
        return CommandBuilder.other_command(Command.EXECUTION_FINISHED, data)

    def _read(self) -> Message | None:
        """Reads data from the UART connection."""
        ser = serial.Serial(self._read_port, 115200, timeout=2.0)
        data = ser.read(23)
        if not data:
            return None

        if data[:4] != b'AAAB':
            print('Invalid preamble')
            return None

        message_data = data[4:]
        return Message.from_buffer_copy(message_data)

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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(simulator.control_simulator)
        executor.submit(simulator.simulate_reader)
        executor.submit(simulator.simulate_execution)
