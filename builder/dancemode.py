"""Implements a special dance mode."""
from uart.command import MoveLift
from uart.commandbuilder import CommandBuilder

from .uartcommunicatorspy import UartCommunicatorSpy


class DanceMode:
    """Performs a special dance mode."""
    def __init__(self) -> None:
        self.communicator = UartCommunicatorSpy()

    def dance(self):
        while True:
            self.communicator.write_uart(CommandBuilder().move_lift(MoveLift.MOVE_DOWN))
            self.communicator.write_uart(CommandBuilder().rotate_grid(100))
            self.communicator.write_uart(CommandBuilder().move_lift(MoveLift.MOVE_UP))


if __name__ == '__main__':
    dancer = DanceMode()
    dancer.dance()
