"""Implements the 3D Re-Builder application."""
import logging
import queue
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Event, Queue

from shared.data import AppConfiguration
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
        self._executor = ProcessPoolExecutor(max_workers=2)
        self._halt_event = Event()
        self._run_in_progress = False

        self._recognition_queue: Queue = Queue()
        self._uart_read: Queue = Queue()
        self._uart_write: Queue = Queue()

        self._cube_api = CubeApi(app_config)
        self._time_measurement = TimeMeasurement()
        self._builder = Builder(self._recognition_queue, self._uart_write)
        self._stream_processing = StreamProcessing(app_config, self._recognition_queue)
        self._uart_communicator = UartCommunicator(app_config, self._uart_read, self._uart_write)

    def start(self) -> None:
        """Starts the rebuilder application processes."""
        self._logger.info('Starting rebuilder application processes')
        self._halt_event.clear()
        self._stream_processing.start()
        self._uart_communicator.start(reader=True, writer=True)
        self._logger.info('Rebuilder application processes started')

    def join(self) -> None:
        """Waits for the rebuilder application processes to complete."""
        self._logger.info('Waiting for rebuilder application processes to complete')
        self._builder.join()
        self._stream_processing.join()
        self._uart_communicator.join(reader=True, writer=True)
        self._logger.info('Rebuilder application processes completed')

    def stop(self) -> None:
        """Stops the rebuilder application processes."""
        self._logger.info('Stopping rebuilder application processes')
        self._builder.stop()
        self._stream_processing.stop()
        self._uart_communicator.stop(reader=True, writer=True)
        self._executor.shutdown()
        self._logger.info('Rebuilder application processes stopped')

    def halt(self) -> None:
        """Halts all processes of the rebuilder application."""
        self._logger.info('Halting rebuilder application processes')
        self._halt_event.set()
        self._builder.halt()
        self._stream_processing.halt()
        self._uart_communicator.halt(reader=True, writer=True)

    def run(self) -> None:
        """Runs the main rebuilder application loop."""
        self._logger.info('Entering main loop')
        while not self._halt_event.is_set():
            self._handle_uart_messages()
            self._processes_alive_check()
        self._logger.info('Exiting main loop')

    def _handle_uart_messages(self) -> None:
        """Handles incoming UART messages."""
        try:
            message = self._uart_read.get(timeout=0.25)
            cmd = Command(message.cmd)
            self._logger.debug('Received UART message: %s', cmd)

            if cmd == Command.SEND_IO_STATE:
                btn_start_state = ButtonState(message.data.send_io_state.btn_start)
                if btn_start_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED):
                    self._start_run()
            if cmd == Command.EXECUTION_FINISHED:
                exec_finished_cmd = Command(message.data.exec_finished.cmd)
                self._logger.info('Finished command: %s', exec_finished_cmd)
                if exec_finished_cmd == Command.MOVE_LIFT:
                    self._uart_write.put(CommandBuilder.other_command(Command.GET_STATE))
            if cmd == Command.SEND_STATE:
                energy = message.data.send_state.energy
                lift_state = LiftState(message.data.send_state.lift_state)
                werni_state = WerniState(message.data.send_state.werni_state)
                if lift_state == LiftState.LIFT_DOWN:
                    self._finish_run()
                    self._uart_write.put(CommandBuilder.enable_buzzer(BuzzerState.ENABLE))
                self._logger.info('State - energy: %sWs, lift: %s, werni: %s', energy, lift_state, werni_state)
        except ValueError as error:
            self._logger.error('Failed to parse UART message: %s', error)
        except queue.Empty:
            pass

    def _processes_alive_check(self) -> None:
        """Checks if all processes are still alive."""
        if not self._builder.halted() and not self._builder.alive():
            self._builder.start()
        if not self._stream_processing.halted() and not self._stream_processing.alive():
            self._stream_processing.start()
        if not self._uart_communicator.halted(reader=True) and not self._uart_communicator.alive(reader=True):
            self._uart_communicator.start(reader=True)
        if not self._uart_communicator.halted(writer=True) and not self._uart_communicator.alive(writer=True):
            self._uart_communicator.start(writer=True)

    def _start_run(self) -> None:
        """Starts a new run if not already one in progress."""
        if self._run_in_progress:
            self._logger.warning('Run already in progress')
            return

        self._logger.info('Starting new run')
        self._run_in_progress = True
        while not self._recognition_queue.empty() and not self._halt_event.is_set():
            self._recognition_queue.get_nowait()
        while not self._uart_read.empty() and not self._halt_event.is_set():
            self._uart_read.get_nowait()
        while not self._uart_write.empty() and not self._halt_event.is_set():
            self._uart_write.get_nowait()

        self._time_measurement.reset()
        self._time_measurement.start()
        self._executor.submit(CubeApi.send_with_retry, self._cube_api.post_start)
        self._uart_write.put(CommandBuilder.other_command(Command.PRIME_MAGAZINE))
        self._uart_write.put(CommandBuilder.other_command(Command.RESET_ENERGY_MEASUREMENT))
        self._builder.start()
        self._stream_processing.start_recognition()

    def _finish_run(self) -> None:
        """Finishes the current run."""
        if not self._run_in_progress:
            self._logger.warning('No run in progress')
            return

        self._logger.info('Finishing current run')
        self._run_in_progress = False
        self._time_measurement.stop()
        self._stream_processing.stop_recognition()
        self._executor.submit(CubeApi.send_with_retry, self._cube_api.post_end)
        self._logger.info('Run completed in %.3fs', self._time_measurement.total_runtime())
        self._executor.submit(CubeApi.send_with_retry, self._cube_api.get_config)
