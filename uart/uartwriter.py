import serial
from time import sleep
from command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState

class uartwriter:
    def __init__(self) -> None:
        self.ser = serial.Serial("/dev/ttys072", 115200)
    
    def close_Connection(self):
        self.ser.close()

    def rotateGrid(self, degrees_h, degrees_l):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        rotate = CmdRotateGrid()
        rotate.degrees_h = degrees_h
        rotate.degrees_l = degrees_l
        union.cmdRotateGrid = rotate
        cmd.cmd = COMMAND.CMD_ROTATE_GRID.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def placeCubes(self, red, yellow, blue):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        place = CmdPlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue
        union.cmdPlaceCubes = place
        cmd.cmd = COMMAND.CMD_PLACE_CUBES.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def moveLift(self, state):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        union.cmdMoveLift = state.value
        cmd.cmd = COMMAND.CMD_MOVE_LIFT.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def sendState(self, dummy1, dummy2, dummy3, dummy4):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.cmd = COMMAND.CMD_SEND_STATE.value
        state = CmdSendState()
        state.dummy1 = dummy1
        state.dummy2 = dummy2
        state.dummy3 = dummy3
        state.dummy4 = dummy4
        union.cmdSendState = state
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def otherCommands(self, command):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.cmd = command.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def encoder(self, command: bytes) -> bytes:
        preamble = b'AAAB'
        return preamble + command

    # Mit den folgenden zwei funktionen hatte ich mühe ich habe die methoden nach dieser webseite programmiert:
    # https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
    def writeToUart(self, cmd):
        self.ser.write(self.encoder(cmd))



if __name__ == '__main__':
    writer = uartwriter()
    #writer.rotateGrid(1, 8)
    #writer.placeCubes(5,8,9)
    #writer.moveLift(CmdMoveLift.MOVE_UP)
    #writer.sendState(1, 3, 5, 7)
    #writer.otherCommands(COMMAND.CMD_ACKNOWLEDGE)


