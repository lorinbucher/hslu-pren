from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from shared.cubecolor import CubeColor

class uartcomunicatorSpy:
    def __init__(self) -> None:
        self.lastresult = None
    

    def write_uart(self, cmd):
        # Start by collecting the basic information
        result = f"Command ID: {cmd.cmd}"
        result += f"Message ID: "
        result += f"Checksum: {cmd.checksum}"

        # Check the type of command and append the relevant data
        if cmd.cmd == COMMAND.CMD_ROTATE_GRID.value:
            result += f"Rotate Grid Degrees: {cmd.dataUnion.cmdRotateGrid.degrees}"
        elif cmd.cmd == COMMAND.CMD_PLACE_CUBES.value:
            result += f"Place Cubes - Red: {cmd.dataUnion.cmdPlaceCubes.cubes_red}, Yellow: {cmd.dataUnion.cmdPlaceCubes.cubes_yellow}, Blue: {cmd.dataUnion.cmdPlaceCubes.cubes_blue}"
        elif cmd.cmd == COMMAND.CMD_MOVE_LIFT.value:
            move_direction = "Up" if cmd.dataUnion.cmdMoveLift == CmdMoveLift.MOVE_UP.value else "Down"
            result += f"Move Lift Direction: {move_direction}"
        elif cmd.cmd == COMMAND.CMD_SEND_STATE.value:
            result += "Send State Data:"
            result += f"  Dummy1: {cmd.dataUnion.cmdSendState.dummy1}"
            result += f"  Dummy2: {cmd.dataUnion.cmdSendState.dummy2}"
            result += f"  Dummy3: {cmd.dataUnion.cmdSendState.dummy3}"
            result += f"  Dummy4: {cmd.dataUnion.cmdSendState.dummy4}"

        print(result)
        self.lastresult = result
