import serial
from time import sleep
from command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message

class UartCommunicator:
    # Die folgenden 3 Methoden geben beispiel befehle an die dann auch in uart gewschrieben werden
    def place(self, red, yellow, blue):
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


    def rotate(self, degrees_h, degrees_l):
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


    def moveLiftUp(self):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        union.cmdMoveLift = CmdMoveLift.MOVE_UP.value
        cmd.cmd = COMMAND.CMD_MOVE_LIFT.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def moveLiftDown(self):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        union.cmdMoveLift = CmdMoveLift.MOVE_UP.value
        cmd.cmd = COMMAND.CMD_MOVE_LIFT.value
        cmd.dataUnion = union
        self.writeToUart(cmd)


    def getState(self):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.cmd = COMMAND.CMD_STATE.value
        cmd.dataUnion = union
        self.writeToUart(cmd)

    def encoder(self, command: bytes) -> bytes:
        preamble = b'AAAB'
        return preamble + command


    # Mit den folgenden zwei funktionen hatte ich mühe ich habe die methoden nach dieser webseite programmiert:
    # https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
    def writeToUart(self, cmd):
        ser = serial.Serial("/dev/ttyAMA0", 115200)

        print(self.encoder(cmd))


        ser.write(self.encoder(cmd))
        ser.close()


    def readFromUart(self):
        ser = serial.Serial("/dev/ttyAMA0", 115200)
        while True:
            received_data = ser.read()
            sleep(0.03)
            data_left = ser.inWaiting()
            received_data += ser.read(data_left)
            print(received_data)


    if __name__ == '__main__':
        moveLiftDown()
        readFromUart()
