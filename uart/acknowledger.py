import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
import time

class acknowledger:
    def __init__(self, write_path):
        self.writer = uartwriter(write_path)

if __name__ == "__main__":
    ack = acknowledger("/dev/ttys073")
    command = commandbuilder().otherCommands(COMMAND.CMD_ACKNOWLEDGE)
    ack.writer.writeToUart(command)
