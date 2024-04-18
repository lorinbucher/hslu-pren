import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
from time import sleep

class uartcommunicator:
    def __init__(self, path="/dev/ttys026"):
        self.reader = uartreader(path)
        self.writer = uartwriter(path)

    
    def read_acknowledge(self):
        while (self.reader.is_empty() == False):
            command = self.reader.get_from_queue()
            action = COMMAND(command.cmd)
            if (action == COMMAND.CMD_ACKNOWLEDGE or action == COMMAND.CMD_NOT_ACKNOWLEDGE):
                return True
        return False
    

    def write_uart(self, cmd):
        self.reader.empty_queue()
        while (self.read_acknowledge() == False):
            self.writer.writeToUart(cmd)
            sleep(3.03)
        

if __name__ == "__main__":
    communicator = uartcommunicator()
    command = commandbuilder().moveLift(CmdMoveLift.MOVE_UP)
    #command = commandbuilder().placeCubes(1, 3, 1)
    #command = commandbuilder().rotateGrid(2, 5)
    #command = commandbuilder().sendState(1, 4, 2, 1)
    communicator.write_uart(command)
    