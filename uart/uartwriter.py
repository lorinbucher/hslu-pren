import serial
from time import sleep
from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState

class uartwriter:
    def __init__(self, path) -> None:
        self.path = path
        

    def encoder(self, command: bytes) -> bytes:
        preamble = b'AAAB'
        return preamble + command

    # Mit den folgenden zwei funktionen hatte ich mühe ich habe die methoden nach dieser webseite programmiert:
    # https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
    def writeToUart(self, cmd):
        print(self.encoder(cmd))
        ser = serial.Serial(self.path, 115200)
        ser.write(self.encoder(cmd))
        ser.close()



if __name__ == '__main__':
    writer = uartwriter("/dev/ttys073")
    writer.rotateGrid(1, 8)
    #writer.placeCubes(5,8,9)
    #writer.moveLift(CmdMoveLift.MOVE_UP)
    #writer.sendState(1, 3, 5, 7)
    #writer.otherCommands(COMMAND.CMD_ACKNOWLEDGE)


