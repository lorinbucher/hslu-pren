from uart.command import Command, CmdMoveLift


class UartCommunicatorSpy:
    def __init__(self) -> None:
        self._last_result = None

    @property
    def last_result(self):
        return self._last_result

    def write_uart(self, cmd):
        # Start by collecting the basic information
        result = f"Command ID: {cmd.cmd}"
        result += "Message ID: "
        result += f"Checksum: {cmd.checksum}"

        # Check the type of command and append the relevant data
        if cmd.cmd == Command.ROTATE_GRID.value:
            result += f"Rotate Grid Degrees: {cmd.dataUnion.cmdRotateGrid.degrees}"
        elif cmd.cmd == Command.PLACE_CUBES.value:
            result += (f"Place Cubes - Red: {cmd.dataUnion.cmdPlaceCubes.cubes_red}, "
                       f"Yellow: {cmd.dataUnion.cmdPlaceCubes.cubes_yellow}, "
                       f"Blue: {cmd.dataUnion.cmdPlaceCubes.cubes_blue}")
        elif cmd.cmd == Command.MOVE_LIFT.value:
            move_direction = "Up" if cmd.dataUnion.cmdMoveLift == CmdMoveLift.MOVE_UP.value else "Down"
            result += f"Move Lift Direction: {move_direction}"
        elif cmd.cmd == Command.SEND_STATE.value:
            result += "Send State Data:"
            result += f"  Dummy1: {cmd.dataUnion.cmdSendState.dummy1}"
            result += f"  Dummy2: {cmd.dataUnion.cmdSendState.dummy2}"
            result += f"  Dummy3: {cmd.dataUnion.cmdSendState.dummy3}"
            result += f"  Dummy4: {cmd.dataUnion.cmdSendState.dummy4}"

        print(result)
        self._last_result = result
