"""Implements the reader for the UART communication protocol."""
import threading
from queue import Queue
from time import sleep

import serial

from .command import Command, MoveLift, Message


class UartReader:
    """Reads data from the UART interface."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.commands: Queue = Queue()
        thread_reader = threading.Thread(target=self.read)
        thread_reader.start()

    def empty_queue(self):
        while not self.commands.empty():
            self.commands.get()

    def is_empty(self):
        return self.commands.empty()

    def get_from_queue(self):
        return self.commands.get()

    def read(self):
        ser = serial.Serial(self.path, 115200)
        while True:
            received_data = ser.read()
            sleep(0.03)
            data_left = ser.inWaiting()
            received_data += ser.read(data_left)
            command = self.decoder(received_data)
            if command is not None:
                self.commands.put(command)

    def decoder(self, received_data):
        if len(received_data) != 23:
            print('Incomplete data received')
            return None

        preamble = received_data[:4]
        if preamble != b'AAAB':
            print('Invalid preamble')
            return None

        message_data = received_data[4:]
        message = Message.from_buffer_copy(message_data)
        command_type = Command(message.cmd)

        # Access the union data safely
        if command_type == Command.ACKNOWLEDGE:
            print('Acknowledged')
        elif command_type == Command.NOT_ACKNOWLEDGE:
            print('Not Acknowledged')
        elif command_type == Command.CRC_ERROR:
            print('CRC Error')
        elif command_type == Command.ROTATE_GRID:
            rotate_data = message.dataUnion.cmdRotateGrid
            print(f'Rotate Grid: {rotate_data.degrees_h} degrees high, {rotate_data.degrees_l} degrees low')
        elif command_type == Command.PLACE_CUBES:
            place_data = message.dataUnion.cmdPlaceCubes
            print(f'Place Cubes: Red {place_data.cubes_red}, '
                  f'Yellow {place_data.cubes_yellow}, '
                  f'Blue {place_data.cubes_blue}')
        elif command_type == Command.MOVE_LIFT:
            move_data = message.dataUnion.cmdMoveLift
            move_direction = 'Up' if move_data == MoveLift.MOVE_UP.value else 'Down'
            print(f'Move Lift: {move_direction}')
        elif command_type == Command.GET_STATE:
            print('Get State Command')
        elif command_type == Command.SEND_STATE:
            state_data = message.dataUnion.cmdSendState
            print(f'State Data: dummy1 {state_data.dummy1}, '
                  f'dummy2 {state_data.dummy2}, '
                  f'dummy3 {state_data.dummy3}, '
                  f'dummy4 {state_data.dummy4}')
        elif command_type == Command.PAUSE_BUILD:
            print('Pause Build Command')
        elif command_type == Command.RESUME_BUILD:
            print('Resume Build Command')
        else:
            print('Unknown Command')

        return message
