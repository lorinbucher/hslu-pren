import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
import time

if __name__ == "__main__":
    writer = uartwriter("/dev/ttys073")
    command = commandbuilder().otherCommands(COMMAND.CMD_ACKNOWLEDGE)
    writer.writeToUart(command)
