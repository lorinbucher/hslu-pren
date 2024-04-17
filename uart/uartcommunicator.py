import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
import time

class uartcommunicator:
    def __init__(self, read_path="/dev/ttys072", write_path="/dev/ttys073"):
        self.reader = uartreader(read_path)
        self.writer = uartwriter(write_path)
        self.acklowedged = False
        self.thread_reader = threading.Thread(target=self.read_uart)
    
    def read_uart(self):
        command, message = self.reader.readFromUart()
        if command.value == 1:
            self.acklowedged = True
        else:
            self.acklowedged = False

    def write_uart(self):
        self.thread_reader.start()
        self.thread_reader.join()
        if self.acklowedged:
            self.writer.moveLift(CmdMoveLift.MOVE_UP)

if __name__ == "__main__":
    communicator = uartcommunicator()
    communicator.write_uart()
    