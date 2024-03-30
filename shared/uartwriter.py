import serial
import ctypes
from time import sleep
from command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message

#Die folgenden 3 Methoden geben beispiel befehle an die dann auch in uart gewschrieben werden
def place(red, yellow, blue):
    union = DataUnion()
    cmd = Message()
    cmd.checksum = 12
    place = CmdPlaceCubes()
    place.cubes_red = red
    place.cubes_yellow = yellow
    place.cubes_blue = blue
    union.cmdPlaceCubes = place
    cmd.cmd = COMMAND.CMD_PLACE_CUBES.value
    cmd.len = ctypes.sizeof(CmdPlaceCubes)
    cmd.dataUnion = union
    return cmd

def rotate(degrees):
    union = DataUnion()
    cmd = Message()
    cmd.checksum = 12
    rotate = CmdRotateGrid()
    rotate.degrees_h = degrees
    rotate.degrees_l = degrees
    union.cmdRotateGrid = rotate
    cmd.cmd = COMMAND.CMD_ROTATE_GRID.value
    cmd.len = ctypes.sizeof(CmdRotateGrid)
    cmd.dataUnion = union
    return cmd

def moveLiftDown():
    union = DataUnion()
    cmd = Message()
    cmd.checksum = 12
    union.cmdMoveLift = CmdMoveLift.MOVE_DOWN.value
    cmd.cmd = COMMAND.CMD_MOVE_LIFT.value
    cmd.len = ctypes.sizeof(CmdRotateGrid)
    cmd.dataUnion = union
    return cmd

#Mit den folgenden zwei funktionen hatte ich mühe ich habe die methoden nach dieser webseite programmiert:
#https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
def writeToUart():
    ser = serial.Serial ("/dev/ttyAMA10", 9600)
    cmd = moveLiftDown()
    cmd_bytes = bytes(cmd)
    ser.write(cmd_bytes)
    ser.close()

def readFromUart():
    ser = serial.Serial ("/dev/ttyAMA10", 9600)
    while True:
        received_data = ser.read()
        sleep(0.03)
        data_left = ser.inWaiting()
        received_data += ser.read(data_left)
        print (received_data)
        ser.write(received_data)
        ser.close()


#writeToUart()

#readFromUart()