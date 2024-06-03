"""Implements the 3D Re-Builder application."""
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from multiprocessing import Event, Queue

from shared.data import AppConfiguration, CubeConfiguration
from uart.command import ButtonState, BuzzerState, Command, LiftState, WerniState
from uart.commandbuilder import CommandBuilder
from uart.communicator import UartCommunicator
from video.processing import StreamProcessing
from web.api import CubeApi
from .builder import Builder
from .measure import TimeMeasurement


class RebuilderApplication:
    """The main application of the 3D Re-Builder."""

    def __init__(self, app_config: AppConfiguration):
        self._logger = logging.getLogger('rebuilder.app')
        self._app_config = app_config
        self._executor = ThreadPoolExecutor(max_workers=8)
        self._halt_event = Event()
        self._run_in_progress = False
        self._run_paused = False

        self._recognition_queue: Queue = Queue()
        self._uart_read: Queue = Queue()
        self._uart_write: Queue = Queue()

        self._builder = Builder(self._uart_write)
        self._cube_api = CubeApi(app_config)
        self._time = TimeMeasurement()

        self._stream_processing = StreamProcessing(app_config, self._recognition_queue)
        self._uart_communicator = UartCommunicator(app_config, self._uart_read, self._uart_write)

    def start(self) -> None:
        """Starts the rebuilder application processes."""
        self._logger.info('Starting rebuilder application processes')
        self._halt_event.clear()
        self._stream_processing.start()
        self._uart_communicator.start(reader=True, writer=True)
        self._executor.submit(self._handle_uart_messages)
        self._executor.submit(self._process_recognition_result)
        self._executor.submit(self._processes_alive_check)
        self._logger.info('Rebuilder application processes started')

    def join(self) -> None:
        """Waits for the rebuilder application processes to complete."""
        self._logger.info('Waiting for rebuilder application processes to complete')
        while not self._halt_event.is_set():
            time.sleep(1.0)
            if self._stream_processing.alive():
                self._stream_processing.join()
            if self._uart_communicator.alive(reader=True, writer=True):
                self._uart_communicator.join(reader=True, writer=True)
        self._logger.info('Rebuilder application processes completed')

    def stop(self) -> None:
        """Stops the rebuilder application processes."""
        self._logger.info('Stopping rebuilder application processes')
        self._stream_processing.stop()
        self._uart_communicator.stop(reader=True, writer=True)
        self._cube_api.shutdown()
        self._executor.shutdown()
        self._logger.info('Rebuilder application processes stopped')

    def halt(self) -> None:
        """Halts all processes of the rebuilder application."""
        self._logger.info('Halting rebuilder application processes')
        self._halt_event.set()
        self._stream_processing.halt()
        self._uart_communicator.halt(reader=True, writer=True)

    def _handle_uart_messages(self) -> None:
        """Handles incoming UART messages."""
        self._logger.info('Entering UART message handling loop')
        while not self._halt_event.is_set():
            try:
                message = self._uart_read.get(timeout=1.0)
                cmd = Command(message.cmd)
                self._logger.debug('Received UART message: %s', cmd)

                if cmd == Command.SEND_IO_STATE:
                    btn_stop_state = ButtonState(message.data.send_io_state.btn_stop)
                    if btn_stop_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED):
                        self._logger.info('Pausing build')
                        self._run_paused = True
                        self._uart_write.put(CommandBuilder.other_command(Command.PAUSE_BUILD))
                    btn_start_state = ButtonState(message.data.send_io_state.btn_start)
                    if btn_start_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED):
                        if self._run_paused:
                            self._logger.info('Resuming build')
                            self._run_paused = False
                            self._uart_write.put(CommandBuilder.other_command(Command.RESUME_BUILD))
                        else:
                            self._start_run()
                if cmd == Command.EXECUTION_FINISHED:
                    exec_finished_cmd = Command(message.data.exec_finished.cmd)
                    self._logger.info('Finished command: %s', exec_finished_cmd)
                    if exec_finished_cmd == Command.MOVE_LIFT:
                        self._uart_write.put(CommandBuilder.other_command(Command.GET_STATE))
                if cmd == Command.SEND_STATE:
                    energy = self._convert_energy(message.data.send_state.energy)
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
                continue

            if not isinstance(config, CubeConfiguration):
                self._logger.warning('Received data has wrong type: %s', type(config))
                return

            if config.completed():
                self._logger.info('Received complete configuration: %s', config.to_dict())
                self._time.stop_config()
                self._cube_api.submit(self._cube_api.post_config, config, datetime.now())
                self._builder.set_config(config.config)
                self._builder.build(build_doubles_first=True)

        self._logger.info('Exiting recognition result processing loop')

    def _processes_alive_check(self) -> None:
        """Checks if all processes are still alive."""
        self._logger.info('Entering processes alive check loop')
        while not self._halt_event.is_set():
            time.sleep(1)
            if not self._stream_processing.halted() and not self._stream_processing.alive():
                self._stream_processing.start()
            if not self._uart_communicator.halted(reader=True) and not self._uart_communicator.alive(reader=True):
                self._uart_communicator.start(reader=True)
            if not self._uart_communicator.halted(writer=True) and not self._uart_communicator.alive(writer=True):
                self._uart_communicator.start(writer=True)

        self._logger.info('Exiting processes alive check loop')

    def _start_run(self) -> None:
        """Starts a new run if not already one in progress."""
        if self._run_in_progress:
            self._logger.warning('Run already in progress')
            return

        self._logger.info('Starting new run')
        self._run_in_progress = True
        try:
            while not self._recognition_queue.empty() and not self._halt_event.is_set():
                self._recognition_queue.get_nowait()
            while not self._uart_read.empty() and not self._halt_event.is_set():
                self._uart_read.get_nowait()
            while not self._uart_write.empty() and not self._halt_event.is_set():
                self._uart_write.get_nowait()
        except queue.Empty:
            pass

        self._builder.reset()
        self._time.reset()
        self._time.start()
        self._cube_api.submit(self._cube_api.post_start)
        self._uart_write.put(CommandBuilder.other_command(Command.PRIME_MAGAZINE))
        self._uart_write.put(CommandBuilder.other_command(Command.RESET_ENERGY_MEASUREMENT))
        self._stream_processing.start_recognition()

    def _finish_run(self) -> None:
        """Finishes the current run."""
        if not self._run_in_progress:
            self._logger.warning('No run in progress')
            return

        self._logger.info('Finishing current run')
        self._run_in_progress = False
        self._time.stop()
        self._stream_processing.stop_recognition()
        self._cube_api.submit(self._cube_api.post_end)
        self._cube_api.submit(self._cube_api.get_config)
        self._logger.info('Run completed - config: %.3fs, total: %.3fs', self._time.config, self._time.total)
        self._executor.submit(self._buzzer)

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
