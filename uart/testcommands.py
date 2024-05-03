from uart.uartcommunicator import uartcommunicator
from uart.commandbuilder import commandbuilder
import serial
from time import sleep
from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState

if __name__ == "__main__":
    communicator = uartcommunicator("/dev/tty.usbmodem142103")
    #communicator.write_uart(commandbuilder().moveLift(CmdMoveLift.MOVE_UP))
    #communicator.write_uart(commandbuilder().placeCubes(1, 0, 0))
    communicator.write_uart(commandbuilder().rotateGrid(-90))
    #communicator.write_uart(commandbuilder().placeCubes(1, 1, 1))
    #communicator.write_uart(commandbuilder().moveLift(CmdMoveLift.MOVE_DOWN))

    