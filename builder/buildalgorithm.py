from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy

class buildalgorithm:
    def __init__(self, communicator = uartcomunicatorSpy()) -> None:
        self.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self.communicator = communicator
        self.placed = [False, False, False, False, False, False, False, False]
        self.config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
    
    # TBD Prüfung ob conffig sein kann oder ob ein cube unter einem anderen ist



    def match(self, bottom):
        c = [False, False, False, False]
        for i in range(len(c)):
            if bottom:
                if self.pos[i] == self.config[i]:
                    c[i] = True
            else:
                if self.pos[i] == self.config[i+4]:
                    c[i] = True
        self.placeCubes(c)

    def placeCubes(self, conf):
        c = conf
        red = 0
        blue = 0
        yellow = 0
        for i in range(len(c)):
            if c[i]:
                if self.pos[i] == CubeColor.RED:
                    red = 1
                elif self.pos[i] == CubeColor.YELLOW:
                    yellow = 1
                elif self.pos[i] == CubeColor.BLUE:
                    blue = 1
        self.communicator.write_uart(commandbuilder().placeCubes(red, yellow, blue))
        

    def rotateTimes(self, times):
        anlge = times * 90
        self.communicator.write_uart(commandbuilder().rotateGrid(anlge))
        self.pos = self.moveArrayLeft(self.pos)

    # Bis hier getestet, der rest muss noch

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