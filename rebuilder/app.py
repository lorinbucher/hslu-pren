"""Implements the 3D Re-Builder application."""
import logging
import multiprocessing
import queue
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Event

from shared.data import AppConfiguration, CubeConfiguration, StatusData
from shared.enumerations import Action, Status
from uart.command import ButtonState, BuzzerState, Command, LiftState, MoveLift, WerniState
from uart.commandbuilder import CommandBuilder
from uart.communicator import UartCommunicator
from video.processing import StreamProcessing
from web.api import CubeApi
from web.server import WebServer
from .builder import Builder


class RebuilderApplication:
    """The main application of the 3D Re-Builder."""

    def __init__(self, app_config: AppConfiguration):
        self._logger = logging.getLogger('rebuilder.app')
        self._app_config = app_config
        self._executor = ThreadPoolExecutor(max_workers=8)
        self._halt_event = Event()

        self._recognition_queue: multiprocessing.Queue = multiprocessing.Queue()
        self._uart_read: queue.Queue = queue.Queue()
        self._uart_write: queue.Queue = queue.Queue()
        self._web_queue: queue.Queue = queue.Queue()

        self._builder = Builder(self._uart_write)
        self._cube_api = CubeApi(app_config)
        self._status = StatusData()
        self._webserver = WebServer(self._web_queue, self._status)

        self._stream_processing = StreamProcessing(app_config, self._recognition_queue)
        self._uart_communicator = UartCommunicator(app_config, self._uart_read, self._uart_write)

    def start(self) -> None:
        """Starts the rebuilder application processes."""
        self._logger.info('Starting rebuilder application processes')
        self._halt_event.clear()
        self._webserver.start()
        self._uart_communicator.start()
        self._executor.submit(self._handle_web_actions)
        self._executor.submit(self._handle_uart_messages)
        self._executor.submit(self._process_recognition_result)
        self._logger.info('Rebuilder application processes started')

    def join(self) -> None:
        """Waits for the rebuilder application processes to complete."""
        self._logger.info('Waiting for rebuilder application processes to complete')
        while not self._halt_event.is_set():
            time.sleep(1.0)
        self._logger.info('Rebuilder application processes completed')

    def stop(self) -> None:
        """Stops the rebuilder application processes."""
        self._logger.info('Stopping rebuilder application processes')
        self._cube_api.shutdown()
        self._executor.shutdown()
        self._stream_processing.stop()
        self._uart_communicator.shutdown()
        self._logger.info('Rebuilder application processes stopped')

    def halt(self) -> None:
        """Halts all processes of the rebuilder application."""
        self._logger.info('Halting rebuilder application processes')
        self._halt_event.set()
        self._stream_processing.halt()
        self._uart_communicator.halt()

    def _handle_web_actions(self) -> None:
        """Handles incoming web actions."""
        self._logger.info('Entering web actions handling loop')
        while not self._halt_event.is_set():
            try:
                action = self._web_queue.get(timeout=1.0)
                if isinstance(action, Action):
                    self._logger.info('Received web action: %s', action)
                    if action == Action.INIT and self._status.status in (Status.IDLE, Status.COMPLETED):
                        self._uart_write.put(CommandBuilder.other_command(Command.PRIME_MAGAZINE))
                        self._uart_write.put(CommandBuilder.move_lift(MoveLift.MOVE_UP))
                        self._stream_processing.start()
                        self._status.reset()
                        self._status.status = Status.READY
                    elif action in (Action.START, Action.STOP):
                        self._handle_start_stop(start=action == Action.START, stop=action == Action.STOP)
                    elif action == Action.RESTART:
                        self._logger.info('Restarting application')
                        subprocess.run(['systemctl', 'restart', 'pren-rebuilder.service'], check=False)
                    elif action == Action.REBOOT:
                        self._logger.info('Rebooting operating system')
                        subprocess.run(['systemctl', 'reboot'], check=False)
                    elif action == Action.RESET:
                        self._uart_write.put(CommandBuilder.other_command(Command.RESET_WERNI))
                else:
                    self._logger.warning('Received data has wrong type: %s', type(action))
            except queue.Empty:
                pass

        self._logger.info('Exiting web actions handling loop')

    def _handle_uart_messages(self) -> None:
        """Handles incoming UART messages."""
        self._logger.info('Entering UART message handling loop')
        while not self._halt_event.is_set():
            try:
                message = self._uart_read.get(timeout=1.0)
                cmd = Command(message.cmd)
                self._logger.debug('Received UART message: %s', cmd)

                if cmd == Command.SEND_IO_STATE:
                    btn_start_state = ButtonState(message.data.send_io_state.btn_start)
                    btn_stop_state = ButtonState(message.data.send_io_state.btn_stop)
                    start = btn_start_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED)
                    stop = btn_stop_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED)
                    self._handle_start_stop(start, stop)
                if cmd == Command.EXECUTION_FINISHED:
                    exec_finished = Command(message.data.exec_finished.cmd)
                    self._logger.info('Finished command: %s', exec_finished)
                    if exec_finished == Command.MOVE_LIFT and self._status.status in (Status.RUNNING, Status.PAUSED):
                        self._uart_write.put(CommandBuilder.other_command(Command.GET_STATE))
                if cmd == Command.SEND_STATE:
                    energy = self._convert_energy(message.data.send_state.energy)
                    self._status.energy = energy
                    lift_state = LiftState(message.data.send_state.lift_state)
                    werni_state = WerniState(message.data.send_state.werni_state)
                    if lift_state == LiftState.LIFT_DOWN:
                        self._finish_run()
                    self._logger.info('State - energy: %.3fWh, lift: %s, werni: %s', energy, lift_state, werni_state)
            except ValueError as error:
                self._logger.error('Failed to parse UART message: %s', error)
            except queue.Empty:
                pass

        self._logger.info('Exiting UART message handling loop')

    def _process_recognition_result(self) -> None:
        """Processes the cube recognition results."""
        self._logger.info('Entering recognition result processing loop')
        while not self._halt_event.is_set():
            try:
                config = self._recognition_queue.get(timeout=1.0)
            except queue.Empty:
                if self._status.status in (Status.RUNNING, Status.PAUSED) and not self._builder.is_running:
                    current_runtime = (time.time_ns() - self._status.time_start) / 1_000_000_000
                    if current_runtime > self._app_config.app_recognition_timeout:
                        self._logger.warning('Recognition timeout passed, building default config')
                        config = CubeConfiguration()
                        config.set_default()
                        self._recognition_queue.put(config)
                continue

            if not isinstance(config, CubeConfiguration):
                self._logger.warning('Received data has wrong type: %s', type(config))
                return

            self._status.config = config.config
            if config.completed():
                self._logger.info('Received complete configuration: %s', config.to_dict())
                self._status.time_config = time.time_ns()
                self._cube_api.submit(self._cube_api.post_config, config, datetime.now())
                self._builder.set_config(config.config)
                self._builder.build(build_doubles_first=True)
                self._stream_processing.halt()
                self._stream_processing.stop_recognition()

        self._logger.info('Exiting recognition result processing loop')

    def _handle_start_stop(self, start: bool = False, stop: bool = False) -> None:
        """Handles start and stop signals."""
        if stop:
            self._logger.info('Pausing build')
            self._status.status = Status.PAUSED
            self._uart_write.put(CommandBuilder.other_command(Command.PAUSE_BUILD))
        elif start:
            if self._status.status == Status.PAUSED:
                self._logger.info('Resuming build')
                self._status.status = Status.RUNNING
                self._uart_write.put(CommandBuilder.other_command(Command.RESUME_BUILD))
            elif self._status.status == Status.READY:
                self._start_run()
            else:
                self._logger.warning('Run not initialized yet')

    def _start_run(self) -> None:
        """Starts a new run if not already one in progress."""
        if self._status.status in (Status.RUNNING, Status.PAUSED):
            self._logger.warning('Run already in progress')
            return

        self._logger.info('Starting new run')
        self._status.status = Status.RUNNING
        self._builder.reset()
        self._status.time_start = time.time_ns()
        self._cube_api.submit(self._cube_api.post_start)
        self._uart_write.put(CommandBuilder.other_command(Command.RESET_ENERGY_MEASUREMENT))
        self._stream_processing.start_recognition()

    def _finish_run(self) -> None:
        """Finishes the current run."""
        if self._status.status not in (Status.RUNNING, Status.PAUSED):
            self._logger.warning('No run in progress')
            return

        self._logger.info('Finishing current run')
        self._status.status = Status.COMPLETED
        self._status.time_end = time.time_ns()
        self._stream_processing.stop()
        self._cube_api.submit(self._cube_api.post_end)
        self._cube_api.submit(self._cube_api.get_config)
        self._executor.submit(self._buzzer)
        self._logger.info('Run completed - config: %.3fs, total: %.3fs',
                          self._status.duration_config, self._status.duration_total)

    def _buzzer(self) -> None:
        """Marks the end of the run with the buzzer for a few seconds."""
        self._uart_write.put(CommandBuilder.enable_buzzer(BuzzerState.ENABLE))
        time.sleep(10)
        self._uart_write.put(CommandBuilder.enable_buzzer(BuzzerState.DISABLE))

    def _convert_energy(self, energy: float) -> float:
        """Converts the energy measurement into Wh."""
        multiplier = 1.0
        if self._app_config.app_efficiency_mode:
            multiplier = 0.5
        return (energy / 3600) * multiplier
