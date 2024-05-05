"""Implements a simulation of the UART communication for the unit tests."""
from uart.command import Command, CmdMoveLift


class UartCommunicatorSpy:
    """Simulates the UART communication for the unit tests."""
    def __init__(self) -> None:
        self._last_result = None

    @property
    def last_result(self):
        return self._last_result

    def write_uart(self, cmd):
        # Start by collecting the basic information
        result = f'Command ID: {cmd.cmd}'
        result += 'Message ID: '
        result += f'Checksum: {cmd.checksum}'

        # Check the type of command and append the relevant data
        if cmd.cmd == Command.ROTATE_GRID.value:
            result += f'Rotate Grid Degrees: {cmd.data_union.cmd_rotate_grid.degrees}'
        elif cmd.cmd == Command.PLACE_CUBES.value:
            result += (f'Place Cubes - Red: {cmd.data_union.cmd_place_cubes.cubes_red}, '
                       f'Yellow: {cmd.data_union.cmd_place_cubes.cubes_yellow}, '
                       f'Blue: {cmd.data_union.cmd_place_cubes.cubes_blue}')
        elif cmd.cmd == Command.MOVE_LIFT.value:
            move_direction = 'Up' if cmd.data_union.cmd_move_lift == CmdMoveLift.MOVE_UP.value else 'Down'
            result += f'Move Lift Direction: {move_direction}'
        elif cmd.cmd == Command.SEND_STATE.value:
            result += 'Send State Data:'
            result += f'  Dummy1: {cmd.data_union.cmd_send_state.dummy1}'
            result += f'  Dummy2: {cmd.data_union.cmd_send_state.dummy2}'
            result += f'  Dummy3: {cmd.data_union.cmd_send_state.dummy3}'
            result += f'  Dummy4: {cmd.data_union.cmd_send_state.dummy4}'

        print(result)
        self._last_result = result
