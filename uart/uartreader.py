from ctypes import POINTER, c_uint8, sizeof
import threading
from typing import cast
import serial
from time import sleep
from uart.command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message
from queue import Queue


class uartreader:
    def __init__(self, path) -> None:
        self.path = path
        self.commands = Queue()
        thread_reader = threading.Thread(target=self.readFromUart)
        thread_reader.start()

    def empty_queue(self):
        while (not self.commands.empty()):
            self.commands.get()

    def is_empty(self):
        return self.commands.empty()

    def get_from_queue(self):
        return self.commands.get()
        

    def readFromUart(self):
        ser = serial.Serial(self.path, 115200)
        while True:
            received_data = ser.read()
            sleep(0.03)
            data_left = ser.inWaiting()
            received_data += ser.read(data_left)
            command = self.decoder(received_data)
            if (command is not None):
                self.commands.put(command)
        

    def decoder(self, received_data):
        if len(received_data) != 23:
            print("Incomplete data received")
            return None

        preamble = received_data[:4]
        if preamble != b'AAAB':
            print("Invalid preamble")
            return None

        message_data = received_data[4:]
        message = Message.from_buffer_copy(message_data)
        command_type = COMMAND(message.cmd)

        #print(f"Command: {command_type.name}")

        # Access the union data safely
        if command_type == COMMAND.CMD_ACKNOWLEDGE:
            print("Acknowledged")
        elif command_type == COMMAND.CMD_NOT_ACKNOWLEDGE:
            print("Not Acknowledged")
        elif command_type == COMMAND.CMD_CRC_ERROR:
            print("CRC Error")
        elif command_type == COMMAND.CMD_ROTATE_GRID:
            rotate_data = message.dataUnion.cmdRotateGrid
            print(f"Rotate Grid: {rotate_data.degrees_h} degrees high, {rotate_data.degrees_l} degrees low")
        elif command_type == COMMAND.CMD_PLACE_CUBES:
            place_data = message.dataUnion.cmdPlaceCubes
            print(f"Place Cubes: Red {place_data.cubes_red}, Yellow {place_data.cubes_yellow}, Blue {place_data.cubes_blue}")
        elif command_type == COMMAND.CMD_MOVE_LIFT:
            move_data = message.dataUnion.cmdMoveLift
            move_direction = "Up" if move_data == CmdMoveLift.MOVE_UP.value else "Down"
            print(f"Move Lift: {move_direction}")
        elif command_type == COMMAND.CMD_GET_STATE:
            print("Get State Command")
        elif command_type == COMMAND.CMD_SEND_STATE:
            state_data = message.dataUnion.cmdSendState
            print(f"State Data: dummy1 {state_data.dummy1}, dummy2 {state_data.dummy2}, dummy3 {state_data.dummy3}, dummy4 {state_data.dummy4}")
        elif command_type == COMMAND.CMD_PAUSE_BUILD:
            print("Pause Build Command")
        elif command_type == COMMAND.CMD_RESUME_BUILD:
            print("Resume Build Command")
        else:
            print("Unknown Command")

        return message


if __name__ == '__main__':
    reader = uartreader("/dev/ttys072")
    reader.readFromUart()

