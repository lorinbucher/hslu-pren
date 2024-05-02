from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from shared.cubecolor import CubeColor

class uartcomunicatorSpy:
    def __init__(self) -> None:
        self.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        pass
    

    def write_uart(self, cmd):
        pass