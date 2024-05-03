import threading
from uart.uartreader import uartreader
from uart.uartwriter import uartwriter
from uart.command import COMMAND, Message, CmdMoveLift
from uart.commandbuilder import commandbuilder
from time import sleep

class uartcommunicator:
    def __init__(self, path):
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
        


    