import threading
from uartreader import uartreader
from uartwriter import uartwriter
from command import COMMAND, Message, CmdMoveLift
from commandbuilder import commandbuilder
import time

class electronicsimulator:
    def __init__(self, path) -> None:
        self.writer = uartwriter(path)
        self.reader = uartreader(path)

    def acknowledge(self):
        command = commandbuilder().otherCommands(COMMAND.CMD_ACKNOWLEDGE)
        self.writer.writeToUart(command)

    def notacknowledge(self):
        command = commandbuilder().otherCommands(COMMAND.CMD_NOT_ACKNOWLEDGE)
        self.writer.writeToUart(command)

    def checksumerror(self):
        command = commandbuilder().otherCommands(COMMAND.CMD_CRC_ERROR)
        self.writer.writeToUart(command)

    def disturb(self):
        pass

    def simulate(self):
        while True:
            command = int(input("1 ack, 2 nack, 3 crc"))
            if command == 1:
                self.acknowledge()
            elif command == 2:
                self.notacknowledge()
            elif command == 3:
                self.checksumerror()

    

if __name__ == "__main__":
    sim = electronicsimulator("/dev/ttys017")
    sim.simulate()
