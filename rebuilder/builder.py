"""Implements the build algorithm."""
import logging
import queue
from enum import Enum
from multiprocessing import Event, Process, Queue

from shared.data import CubeConfiguration
from shared.enumerations import CubeColor
from uart.command import MoveLift
from uart.commandbuilder import CommandBuilder


class CubeState(Enum):
    """The cube states."""
    UNKNOWN = 0
    NOTPLACED = 1
    PLACED = 2


class Builder:
    """Sends the commands using the UART communication protocol to build the detected cube configuration."""

    def __init__(self, builder_queue: Queue, uart_write: Queue) -> None:
        self._logger = logging.getLogger('rebuilder.builder')
        self._halt = Event()
        self._builder_queue = builder_queue
        self._uart_write = uart_write
        self._halt.set()
        self.rotated = 0

        self._process: Process | None = None
        self._config = [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED,
                        CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED]
        self._placed = [False, False, False, False, False, False, False, False]
        self._pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        self._cube_states = [CubeState.UNKNOWN, CubeState.UNKNOWN, CubeState.UNKNOWN, CubeState.UNKNOWN,
                             CubeState.UNKNOWN, CubeState.UNKNOWN, CubeState.UNKNOWN, CubeState.UNKNOWN]

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
                    self.build(build_doubles_first=True)
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
    def cube_states(self) -> list[CubeState]:
        """Returns the cube states."""
        return self._cube_states.copy()

    @property
    def pos(self) -> list[CubeColor]:
        """Returns the current position."""
        return self._pos.copy()

    def set_config(self, config: list[CubeColor]) -> None:
        """Sets the cube configuration."""
        for i in range(4):
            if config[i] == CubeColor.UNKNOWN:
                config[i + 4] = CubeColor.UNKNOWN
        self._config = config

    def build(self, build_doubles_first: bool = False) -> None:
        """Builds the cube configuration, optionally trying to build doubles."""
        if build_doubles_first:
            self.build_doubles()
        self.build_whats_possible()
        self.finish_build()

    def build_doubles(self) -> None:
        """Tries to build doubles if possible."""
        config = [CubeColor.NONE, CubeColor.NONE, CubeColor.NONE, CubeColor.NONE]
        for i in range(4):
            if self._config[i] == self._config[i + 4] and self._config[i] != CubeColor.UNKNOWN:
                config[i] = self._config[i]
                self._cube_states[i] = CubeState.PLACED
                self._cube_states[i + 4] = CubeState.PLACED
        self.build_config(config, True)

    def build_whats_possible(self) -> None:
        """Place all cubes that are possible to place."""
        while True:
            self.update_cube_states()
            self.place_not_placed()
            if all(state != CubeState.NOTPLACED for state in self._cube_states):
                break

    def finish_build(self) -> None:
        """Returns the grid to the correct position and moves the lift down."""
        self.rotate_grid(4 - self.rotated, rotate_pos=True)
        self._logger.info('Move lift down command queued')
        self._uart_write.put(CommandBuilder.move_lift(MoveLift.MOVE_DOWN))

    def place_not_placed(self) -> None:
        """Place all cubes that are not placed yet."""
        config = [CubeColor.NONE, CubeColor.NONE, CubeColor.NONE, CubeColor.NONE]
        for i in range(4):
            if self._cube_states[i] == CubeState.NOTPLACED:
                config[i] = self._config[i]
                self._cube_states[i] = CubeState.PLACED
            elif i + 4 < 8 and self._cube_states[i + 4] == CubeState.NOTPLACED:
                config[i] = self._config[i + 4]
                self._cube_states[i + 4] = CubeState.PLACED
        self.build_config(config)

    def update_cube_states(self) -> None:
        """Updates the cube states."""
        for i in range(len(self._config)):
            config = self._config[i]
            if config == CubeColor.NONE:
                self._cube_states[i] = CubeState.PLACED
            elif ((config == CubeColor.RED or config == CubeColor.BLUE or config == CubeColor.YELLOW) and
                  self._cube_states[i] == CubeState.UNKNOWN):
                self._cube_states[i] = CubeState.NOTPLACED

    def build_config(self, initial_config: list[CubeColor], two_cubes: bool = False) -> None:
        """Builds the configuration."""
        config = initial_config.copy()
        while not Builder.config_none(config):
            c, config = self.match_with_config(config)
            times = 0
            while Builder.array_false(c):
                times += 1
                self.move_pos(1)
                c, config = self.match_with_config(config)
            self.rotate_grid(times, rotate_pos=False)
            self.place_cubes(c, two_cubes)

    @staticmethod
    def config_none(config: list[CubeColor]) -> bool:
        """Returns true if the entire cube configuration is empty."""
        return all(c == CubeColor.NONE for c in config)

    def match_with_config(self, config) -> tuple[list[bool], list[CubeColor]]:
        """Returns a list of matches between the configuration and the current position."""
        c = [False, False, False, False]
        new_config = config.copy()
        for i in range(len(c)):
            value = config[i]
            if self._pos[i] == value and not value == CubeColor.NONE:
                c[i] = True
                new_config[i] = CubeColor.NONE
            else:
                new_config[i] = value
        return c, new_config

    def place_cubes(self, conf: list[bool], two_cubes: bool = False) -> None:
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
            if two_cubes:
                red = red * 2
                yellow = yellow * 2
                blue = blue * 2
            self._logger.info('Place cubes command queued - red: %s, yellow: %s, blue: %s', red, yellow, blue)
            self._uart_write.put(CommandBuilder.place_cubes(red, yellow, blue))

    def rotate_grid(self, times: int, rotate_pos: bool = True) -> None:
        """Rotates the grid the specified number of times."""
        if times % 4 != 0:
            angle = times * 90
            self._logger.info('Rotating grid command queued: %s°', angle)
            self._uart_write.put(CommandBuilder.rotate_grid(angle))
            self.rotated = self.rotated + times % 4
            if rotate_pos:
                self.move_pos(times)

    def move_pos(self, times: int) -> None:
        """Rotates the position by the specified number of times."""
        times = times % len(self._pos)
        if times != 0:
            self._pos = self._pos[times:] + self._pos[:times]

    @staticmethod
    def array_false(array: list[bool]) -> bool:
        """Returns true if the entire array is false."""
        return not any(array)
