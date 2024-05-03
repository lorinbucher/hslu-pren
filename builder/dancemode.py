from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from uart.uartcommunicator import uartcommunicator
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy
from builder.layer import Layer

class dancemode:
    def __init__(self) -> None:
        self.communicator = uartcomunicatorSpy()
        # self.communicator = commandbuilder()

    def dance(self):
        while True:
            self.communicator.write_uart(commandbuilder().moveLift(CmdMoveLift.MOVE_DOWN))
            self.communicator.write_uart(commandbuilder().rotateGrid(100))
            self.communicator.write_uart(commandbuilder().moveLift(CmdMoveLift.MOVE_UP))



if __name__ == "__main__":
    dancer = dancemode()

    dancer.dance()