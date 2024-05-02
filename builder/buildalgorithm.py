from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy

class buildalgorithm:
    def __init__(self) -> None:
        self.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self.communicator = uartcomunicatorSpy()
        pass
    

    def write_uart(self, cmd):
        pass
        
    def rotateTimes(self, times):
        anlge = times * 90
        self.communicator.write_uart(commandbuilder().rotateGrid(anlge))
        self.pos = self.moveArrayLeft(self.pos)

    def moveArray(self, times):
        if times > 0:
            self.pos = self.moveArrayLeft(self.pos, times)
        elif times < 0:
            self.pos = self.moveArrayRight(self.pos, times * (-1))

    def moveArrayLeft(self, array, times):
        a = array[:]
        for _ in range(times):
            cache = a[0]
            for i in range(len(a) - 1):
                a[i] = a[i+1]
            a[len(a)-1] = cache
        return a

    def moveArrayRight(self, array, times):
        a = array[:]
        for _ in range(times):
            cache = a[len(a)-1]
            for i in range(len(a) - 1):
                a[len(a)-i-1] = a[len(a)-i-2]
            a[0] = cache
        return a