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
    # wenn ich kein match habe, direkt beim nachsten zwei moven

    # Alle methoden ausser match getestet

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
        if red + blue + yellow > 0: self.communicator.write_uart(commandbuilder().placeCubes(red, yellow, blue))
        
    # Folgende Methoden sind super getestet

    def rotateTimes(self, times):
        anlge = times * 90
        self.communicator.write_uart(commandbuilder().rotateGrid(anlge))
        self.movePos(times)


    def movePos(self, times):
        if times > 0:
            self.pos = buildalgorithm.moveArrayLeft(self.pos, times)
        elif times < 0:
            timesabs = abs(times)
            self.pos = buildalgorithm.moveArrayRight(self.pos, timesabs)
        else:
            self.pos = self.pos

    def moveArrayLeft(array, times):
        a = array[:]
        for _ in range(times):
            cache = a[0]
            for i in range(len(a) - 1):
                a[i] = a[i+1]
            a[len(a)-1] = cache
        return a

    def moveArrayRight(array, times):
        a = array[:]
        for _ in range(times):
            cache = a[len(a)-1]
            for i in range(len(a) - 1):
                a[len(a)-i-1] = a[len(a)-i-2]
            a[0] = cache
        return a