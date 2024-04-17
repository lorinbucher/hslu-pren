import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
import time

if __name__ == "__main__":
    reader = uartreader("/dev/ttys073")
    while True:
        reader.readFromUart()
