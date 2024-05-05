"""Implements the build algorithm."""
from shared.enumerations import CubeColor
from uart.command import CmdMoveLift
from uart.commandbuilder import CommandBuilder

from .layer import Layer
from .uartcommunicatorspy import UartCommunicatorSpy


class BuildAlgorithm:
    """Sends the commands using the UART communication protocol to build the detected cube configuration."""

    # Default Config nicht ändern, sonst gehen die unit tests nicht mehr
    def __init__(self, communicator=UartCommunicatorSpy()) -> None:
        self.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self.communicator = communicator
        self.placed = [False, False, False, False, False, False, False, False]
        self.config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW,
                       CubeColor.NONE, CubeColor.RED]

    # Der builder und buildlayer sind nicht unit getestet, aber die funktionalitat sollte stimmen laut dem output.
    # Wenn nur none matched, dann bewegt er sich 90 und dann nochmals 90

    def set_config(self, config):
        self.config = config

    def build(self):
        self.build_layer(Layer.BOTTOM)
        self.communicator.write_uart(CommandBuilder().move_lift(CmdMoveLift.MOVE_DOWN))
        self.build_layer(Layer.TOP)
        self.placed = [False] * len(self.placed)

    def build_layer(self, layer):
        while not self.full_placed_check(layer):
            config = self.match(layer)
            times = 0
            while BuildAlgorithm.array_false_check(config):
                times += 1
                self.move_pos(1)
                config = self.match(layer)
            self.rotate_times_no_array_movement(times)
            self.update_placed(layer, config)
            self.place_cubes(config)

    # Ab hier habe ich mit unit tests getestet

    def full_placed_check(self, layer):
        if layer == Layer.BOTTOM:
            offset = 0
        else:
            offset = 4
        for i in range(4):
            if not self.placed[i + offset]:
                return False
        return True

    def update_placed(self, layer, c):
        if layer == Layer.BOTTOM:
            offset = 0
        else:
            offset = 4
        for i in range(len(c)):
            if c[i]:
                self.placed[i + offset] = True

    def match(self, layer):
        c = [False, False, False, False]
        for i in range(len(c)):
            if layer == Layer.BOTTOM:
                if self.pos[i] == self.config[i] and not self.placed[i]:
                    c[i] = True
            else:
                if self.pos[i] == self.config[i + 4] and not self.placed[i + 4]:
                    c[i] = True
        return c

    @staticmethod
    def array_false_check(array):
        return not any(array)

    def place_cubes(self, conf):
        c = conf
        red = 0
        blue = 0
        yellow = 0
        for i in range(len(c)):
            if c[i]:
                if self.pos[i] == CubeColor.RED:
                    red = 1
                elif self.pos[i] == CubeColor.YELLOW:
                    yellow = 1
                elif self.pos[i] == CubeColor.BLUE:
                    blue = 1
        if red + blue + yellow > 0:
            self.communicator.write_uart(CommandBuilder().place_cubes(red, yellow, blue))

    # Folgende Methoden sind super getestet

    def rotate_times(self, times):
        if times != 0:
            angle = times * 90
            self.communicator.write_uart(CommandBuilder().rotate_grid_efficient(angle))
            self.move_pos(times)

    def rotate_times_no_array_movement(self, times):
        if times != 0:
            angle = times * 90
            self.communicator.write_uart(CommandBuilder().rotate_grid_efficient(angle))

    def move_pos(self, times):
        if times > 0:
            self.pos = BuildAlgorithm.move_array_left(self.pos, times)
        elif times < 0:
            times_abs = abs(times)
            self.pos = BuildAlgorithm.move_array_right(self.pos, times_abs)
        else:
            self.pos = self.pos

    @staticmethod
    def move_array_left(array, times):
        a = array[:]
        for _ in range(times):
            cache = a[0]
            for i in range(len(a) - 1):
                a[i] = a[i + 1]
            a[len(a) - 1] = cache
        return a

    @staticmethod
    def move_array_right(array, times):
        a = array[:]
        for _ in range(times):
            cache = a[len(a) - 1]
            for i in range(len(a) - 1):
                a[len(a) - i - 1] = a[len(a) - i - 2]
            a[0] = cache
        return a


if __name__ == "__main__":
    test_communicator = UartCommunicatorSpy()
    builder = BuildAlgorithm(test_communicator)
    builder.build()

    builder.set_config([CubeColor.BLUE, CubeColor.BLUE, CubeColor.BLUE, CubeColor.BLUE,
                        CubeColor.BLUE, CubeColor.BLUE, CubeColor.BLUE, CubeColor.BLUE])
    builder.build()
