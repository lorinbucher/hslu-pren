import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
import time

class uartcommunicator:
    def __init__(self, read_path="/dev/ttys072", write_path="/dev/ttys073"):
        self.reader = uartreader(read_path)
        self.writer = uartwriter(write_path)
        self.acklowedged = False
    
    def read_uart(self):
        command, message = self.reader.readFromUart()
        if command.value == 1:
            self.acklowedged = True
        else:
            self.acklowedged = False
        print(command)

    def write_uart(self, cmd):
        thread_reader = threading.Thread(target=self.read_uart)
        thread_reader.start()
        thread_reader.join()

        thread_reader2 = threading.Thread(target=self.read_uart)
        thread_reader2.start()
        if self.acklowedged:
            self.writer.writeToUart(cmd)
        thread_reader2.join()

if __name__ == "__main__":
    communicator = uartcommunicator()
    command = commandbuilder().moveLift(CmdMoveLift.MOVE_UP)
    communicator.write_uart(command)
    