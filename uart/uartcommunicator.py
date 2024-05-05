from time import sleep

from .command import Command
from .uartreader import UartReader
from .uartwriter import UartWriter


class UartCommunicator:
    def __init__(self, path):
        self.reader = UartReader(path)
        self.writer = UartWriter(path)

    def read_acknowledge(self):
        while not self.reader.is_empty():
            command = self.reader.get_from_queue()
            action = Command(command.cmd)
            if action == Command.ACKNOWLEDGE or action == Command.NOT_ACKNOWLEDGE:
                return True
        return False

    def write_uart(self, cmd):
        self.reader.empty_queue()
        while not self.read_acknowledge():
            self.writer.write(cmd)
            sleep(3.03)
