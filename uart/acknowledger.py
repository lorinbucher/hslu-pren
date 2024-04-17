import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
import time

class acknowledger:
    def __init__(self, write_path):
        self.writer = uartwriter(write_path)

if __name__ == "__main__":
    ack = acknowledger("/dev/ttys073")
    ack.writer.otherCommands(COMMAND.CMD_ACKNOWLEDGE)
