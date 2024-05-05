from .command import Command
from .commandbuilder import CommandBuilder
from .uartreader import UartReader
from .uartwriter import UartWriter


class ElectronicsSimulator:
    def __init__(self, path) -> None:
        self.writer = UartWriter(path)
        self.reader = UartReader(path)

    def acknowledge(self):
        command = CommandBuilder().other_commands(Command.ACKNOWLEDGE)
        self.writer.write(command)

    def not_acknowledge(self):
        command = CommandBuilder().other_commands(Command.NOT_ACKNOWLEDGE)
        self.writer.write(command)

    def checksum_error(self):
        command = CommandBuilder().other_commands(Command.CRC_ERROR)
        self.writer.write(command)

    def disturb(self):
        self.writer.write(b'\x06\x01\x00\x00\x00')

    def simulate(self):
        while True:
            command = int(input("1 ack, 2 nack, 3 crc"))
            if command == 1:
                self.acknowledge()
            elif command == 2:
                self.not_acknowledge()
            elif command == 3:
                self.checksum_error()


if __name__ == "__main__":
    sim = ElectronicsSimulator("/dev/ttys027")
    sim.simulate()
