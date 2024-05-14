"""Implements the build algorithm."""
import logging
import queue
from multiprocessing import Event, Process, Queue

from shared.data import CubeConfiguration
from shared.enumerations import CubeColor
from uart.command import MoveLift
from uart.commandbuilder import CommandBuilder
from .layer import Layer


class Builder:
    """Sends the commands using the UART communication protocol to build the detected cube configuration."""

    def __init__(self, builder_queue: Queue, uart_write: Queue) -> None:
        self._logger = logging.getLogger('builder.builder')
        self._terminate = Event()
        self._builder_queue = builder_queue
        self._uart_write = uart_write

        self._pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self._placed = [False, False, False, False, False, False, False, False]
        self._config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED,
                        CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
        self._process: Process | None = None

    def start(self) -> None:
        """Starts the builder."""
        self._logger.info('Starting builder')
        self._process = Process(target=self._run)
        self._process.start()
        self._logger.info('Builder started')

    def join(self) -> None:
        """Waits for the builder to complete."""
        if self._process is not None:
            self._logger.info('Waiting for builder to complete')
            self._process.join()
            self._logger.info('Builder completed')

    def stop(self) -> None:
        """Stops the builder."""
        if self._process is not None:
            self._logger.info('Stopping builder')
            self._process.close()
            self._process = None
            self._logger.info('Builder stopped')

    def terminate_signal(self) -> None:
        """Sends the terminate event to the UART reader and writer tasks."""
        self._terminate.set()

    def _run(self) -> None:
        """Runs the builder process."""
        self._logger.info('Builder process started')
        while not self._terminate.is_set():
            try:
                config = self._builder_queue.get(timeout=2.0)
                if not isinstance(config, CubeConfiguration):
                    self._logger.warning('Received data has wrong type: %s', type(config))
                    continue

                if config.completed():
                    self._logger.info('Received complete configuration: %s', config.to_dict())
                    self._terminate.set()
            except queue.Empty:
                continue

        self._logger.info('Builder process stopped')

    def reset(self) -> None:
        """Resets the state of the builder."""
        self._pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]
        self._placed = [False, False, False, False, False, False, False, False]
        self._config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED,
                        CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]

    @property
    def pos(self) -> list[CubeColor]:
        """Returns the current position"""
        return self._pos.copy()

    @property
    def placed(self) -> list[bool]:
        """Returns the placed config"""
        return self._placed.copy()

    def set_config(self, config):
        self._config = config

    def build(self):
        self.build_layer(Layer.BOTTOM)
        self._uart_write.put(CommandBuilder.move_lift(MoveLift.MOVE_DOWN))
        self.build_layer(Layer.TOP)
        self._placed = [False] * len(self._placed)

    def build_layer(self, layer):
        while not self.full_placed_check(layer):
            config = self.match(layer)
            times = 0
            while Builder.array_false_check(config):
                times += 1
                self.move_pos(1)
                config = self.match(layer)
            self.rotate_times_no_array_movement(times)
            self.update_placed(layer, config)
            self.place_cubes(config)

    def full_placed_check(self, layer):
        if layer == Layer.BOTTOM:
            offset = 0
        else:
            offset = 4
        for i in range(4):
            if not self._placed[i + offset]:
                return False
        return True

    def update_placed(self, layer, c):
        if layer == Layer.BOTTOM:
            offset = 0
        else:
            offset = 4
        for i in range(len(c)):
            if c[i]:
                self._placed[i + offset] = True

    def match(self, layer):
        c = [False, False, False, False]
        for i in range(len(c)):
            if layer == Layer.BOTTOM:
                if self._pos[i] == self._config[i] and not self._placed[i]:
                    c[i] = True
            else:
                if self._pos[i] == self._config[i + 4] and not self._placed[i + 4]:
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
                if self._pos[i] == CubeColor.RED:
                    red = 1
                elif self._pos[i] == CubeColor.YELLOW:
                    yellow = 1
                elif self._pos[i] == CubeColor.BLUE:
                    blue = 1
        if red + blue + yellow > 0:
            self._uart_write.put(CommandBuilder.place_cubes(red, yellow, blue))

    def rotate_times(self, times):
        if times != 0:
            angle = times * 90
            self._uart_write.put(CommandBuilder.rotate_grid_efficient(angle))
            self.move_pos(times)

    def rotate_times_no_array_movement(self, times):
        if times != 0:
            angle = times * 90
            self._uart_write.put(CommandBuilder.rotate_grid_efficient(angle))

    def move_pos(self, times):
        if times > 0:
            self._pos = self.move_array_left(self._pos, times)
        elif times < 0:
            times_abs = abs(times)
            self._pos = self.move_array_right(self._pos, times_abs)
        else:
            self._pos = self._pos

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
