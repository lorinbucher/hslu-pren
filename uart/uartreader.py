import serial
from time import sleep
from command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message

class uartreader:

    def readFromUart(self):
        ser = serial.Serial("/dev/ttys047", 115200)
        while True:
            received_data = ser.read()
            sleep(0.03)
            data_left = ser.inWaiting()
            received_data += ser.read(data_left)
            print(received_data)

    def decoder(self):
        pass

if __name__ == '__main__':
    reader = uartreader()
    reader.readFromUart()

