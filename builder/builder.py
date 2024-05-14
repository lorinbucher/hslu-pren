"""Implements the build algorithm."""
import logging
import queue
from enum import Enum
from multiprocessing import Event, Process, Queue

from shared.data import CubeConfiguration
from shared.enumerations import CubeColor
from uart.command import MoveLift
from uart.commandbuilder import CommandBuilder


class Layer(Enum):
    """The build lagers."""
    BOTTOM = 0
    TOP = 4


class Builder:
    """Sends the commands using the UART communication protocol to build the detected cube configuration."""

    def __init__(self, builder_queue: Queue, uart_write: Queue) -> None:
        self._logger = logging.getLogger('builder.builder')
        self._halt = Event()
        self._builder_queue = builder_queue
        self._uart_write = uart_write
        self._halt.set()

        self._process: Process | None = None
        self._config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED,
                        CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
        self._placed = [False, False, False, False, False, False, False, False]
        self._pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

    def start(self) -> None:
        """Starts the builder."""
        self._logger.info('Starting builder')
        self.reset()
        self._halt.clear()
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

    def halt(self) -> None:
        """Sends the halt event to builder task."""
        self._logger.info('Halting builder')
        self._halt.set()

    def halted(self) -> bool:
        """Returns true if the halt event is set, false if not."""
        return self._halt.is_set()

    def alive(self) -> bool:
        """Returns true if the builder process is alive, false if not."""
        result = self._process is not None and self._process.is_alive()
        if not result:
            self._logger.warning('Builder not alive')
        return result

    def _run(self) -> None:
        """Runs the builder process."""
        self._logger.info('Builder process started')
        while not self._halt.is_set():
            try:
                config = self._builder_queue.get(timeout=2.0)
                if not isinstance(config, CubeConfiguration):
                    self._logger.warning('Received data has wrong type: %s', type(config))
                    continue

                if config.completed():
                    self._logger.info('Received complete configuration: %s', config.to_dict())
                    self._config = config.config
                    self.build()
                    self._halt.set()
            except queue.Empty:
                continue

        self._logger.info('Builder process stopped')

    def reset(self) -> None:
        """Resets the state of the builder."""
        self._config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED,
                        CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
        self._placed = [False, False, False, False, False, False, False, False]
        self._pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

    @property
    def placed(self) -> list[bool]:
        """Returns the placed config"""
        return self._placed.copy()

    @property
    def pos(self) -> list[CubeColor]:
        """Returns the current position"""
        return self._pos.copy()

    def build(self) -> None:
        """Builds the bottom and top layer of the configuration."""
        self.build_layer(Layer.BOTTOM)
        self.build_layer(Layer.TOP)
        self._logger.info('Move lift down command queued')
        self._uart_write.put(CommandBuilder.move_lift(MoveLift.MOVE_DOWN))

    def build_layer(self, layer: Layer) -> None:
        """Builds a layer."""
        while not self.layer_placed(layer):
            config = self.match(layer)
            times = 0
            while Builder.array_false(config):
                times += 1
                self.move_pos(1)
                config = self.match(layer)
            self.rotate_grid(times, rotate_pos=False)
            self.update_placed(layer, config)
            self.place_cubes(config)

    def layer_placed(self, layer: Layer) -> bool:
        """Returns true if all cubes of a layer have been placed."""
        offset = layer.value
        return all(self._placed[offset: offset + 4])

    def update_placed(self, layer: Layer, c) -> None:
        """Updates the state of the placed cubes."""
        offset = layer.value
        for i in range(len(c)):
            if c[i]:
                self._placed[i + offset] = True

    def match(self, layer: Layer) -> list[bool]:
        """Returns a list of matches between the configuration and the current position."""
        c = [False, False, False, False]
        for i in range(len(c)):
            if self._pos[i] == self._config[i + layer.value] and not self._placed[i + layer.value]:
                c[i] = True
        return c

    def place_cubes(self, conf: list[bool]) -> None:
        """Sends the command to place the cubes."""
        c = conf
        red = 0
        yellow = 0
        blue = 0
        for i in range(len(c)):
            if c[i]:
                if self._pos[i] == CubeColor.RED:
                    red = 1
                elif self._pos[i] == CubeColor.YELLOW:
                    yellow = 1
                elif self._pos[i] == CubeColor.BLUE:
                    blue = 1
        if (red + yellow + blue) > 0:
            self._logger.info('Place cubes command queued - red: %s, yellow: %s, blue: %s', red, yellow, blue)
            self._uart_write.put(CommandBuilder.place_cubes(red, yellow, blue))

    def rotate_grid(self, times: int, rotate_pos: bool = True) -> None:
        """Rotates the grid the specified number of times."""
        if times % 4 != 0:
            angle = times * 90
            self._logger.info('Rotating grid command queued: %s°', angle)
            self._uart_write.put(CommandBuilder.rotate_grid(angle))
            if rotate_pos:
                self.move_pos(times)

    def move_pos(self, times: int) -> None:
        """Rotates the position by the specified number of times."""
        times = times % len(self.pos)
        if times != 0:
            self._pos = self._pos[times:] + self._pos[:times]

    @staticmethod
    def array_false(array: list[bool]) -> bool:
        """Returns true if the entire array is false."""
        return not any(array)
