from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState
from uart.commandbuilder import commandbuilder
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy
from builder.layer import Layer

class buildalgorithm:
    def __init__(self, communicator = uartcomunicatorSpy()) -> None:
        self.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self.communicator = communicator
        self.placed = [False, False, False, False, False, False, False, False]
        self.config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
    
    # Der builder und buildlayer sind nicht unit getestet, aber die funktionalitat sollte stimmen laut dem output.

    def build(self):
        self.buildLayer(Layer.BOTTOM)
        self.communicator.write_uart(commandbuilder().moveLift(CmdMoveLift.MOVE_DOWN))
        self.buildLayer(Layer.TOP)

    def buildLayer(self, layer):
        while self.fullplacedCheck(layer) == False:
            config = self.match(layer)
            times = 0
            while buildalgorithm.arrayFalseCheck(config):
                times += 1
                self.movePos(1)
                config = self.match(layer)
            self.rotateTimesNoArrayMovement(times)
            self.updatePlaced(layer, config)
            self.placeCubes(config)

    # Ab hier habe ich mit unit tests getestet

    def fullplacedCheck(self, layer):
        if layer == Layer.BOTTOM:
            ofset = 0
        else:
            ofset = 4
        for i in range(4):
            if not self.placed[i+ofset]:
                return False
        return True

    def updatePlaced(self, layer, c):
        if layer == Layer.BOTTOM:
            ofset = 0
        else:
            ofset = 4
        for i in range(len(c)):
            if c[i]:
                self.placed[i+ofset] = True


    def match(self, layer):
        c = [False, False, False, False]
        for i in range(len(c)):
            if layer == Layer.BOTTOM:
                if self.pos[i] == self.config[i] and self.placed[i] == False:
                    c[i] = True
            else:
                if self.pos[i] == self.config[i+4] and self.placed[i+4] == False:
                    c[i] = True
        return c

    def arrayFalseCheck(array):
        for i in range(len(array)):
            if array[i]:
                return False
        return True

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
        if times != 0:
            anlge = times * 90
            self.communicator.write_uart(commandbuilder().rotateGrid(anlge))
            self.movePos(times)

    def rotateTimesNoArrayMovement(self, times):
        if times != 0:
            anlge = times * 90
            self.communicator.write_uart(commandbuilder().rotateGrid(anlge))

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
    

if __name__ == "__main__":
    communicator = uartcomunicatorSpy()
    builder = buildalgorithm(communicator)
    builder.build()