"""The main application of the 3D Re-Builder."""
import logging.config
import multiprocessing
import os
import queue
import signal
import subprocess
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
from threading import Event

import shared.config as app_config
from rebuilder.builder import Builder
from rebuilder.measure import TimeMeasurement
from shared.data import AppConfiguration
from uart.command import ButtonState, Command, LiftState, WerniState
from uart.commandbuilder import CommandBuilder
from uart.communicator import UartCommunicator
from video.processing import StreamProcessing
from web.api import CubeApi

CONFIG_FILE = 'config.toml'


def _parse_config() -> dict:
    """Parses the configuration file."""
    # pylint: disable=possibly-used-before-assignment
    try:
        logger.info('Parsing configuration file: %s', CONFIG_FILE)
        with open(CONFIG_FILE, 'rb') as config_file:
            return tomllib.load(config_file)
    except (FileNotFoundError, PermissionError) as error:
        logger.error('Failed to read config.toml file: %s', error)
    except tomllib.TOMLDecodeError as error:
        logger.error('Failed to parse config.toml file: %s', error)
    sys.exit(1)


def _validate_config(conf: AppConfiguration) -> None:
    """Validates the configuration of the application."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Validating configuration file: %s', CONFIG_FILE)
    is_valid, error = conf.validate()
    if is_valid:
        logger.info('Configuration is valid')
    else:
        logger.error('Invalid configuration: %s', error)
        sys.exit(1)


def _signal_handler(signum, _) -> None:
    """Handles signals to gracefully stop the application."""
    # pylint: disable=possibly-used-before-assignment
    if signum in (signal.SIGINT, signal.SIGTERM) and multiprocessing.current_process().name == 'MainProcess':
        logger.info('Shutting down application')
        halt.set()
        builder.halt()
        stream_processing.halt()
        uart_communicator.halt(reader=True, writer=True)


def _handle_uart_messages() -> None:
    """Handles received UART messages."""
    # pylint: disable=possibly-used-before-assignment
    try:
        message = uart_read.get(timeout=0.25)
        cmd = Command(message.cmd)
        logger.debug('Received UART message: %s', cmd)

        if cmd == Command.SEND_IO_STATE:
            btn_start_state = ButtonState(message.data.send_io_state.btn_start)
            if btn_start_state in (ButtonState.SHORT_CLICKED, ButtonState.LONG_CLICKED):
                _start_run()
        if cmd == Command.EXECUTION_FINISHED:
            exec_finished_cmd = Command(message.data.exec_finished.cmd)
            logger.info('Finished command: %s', exec_finished_cmd)
            if exec_finished_cmd == Command.MOVE_LIFT:
                uart_write.put(CommandBuilder.other_command(Command.GET_STATE))
        if cmd == Command.SEND_STATE:
            energy = message.data.send_state.energy
            lift_state = LiftState(message.data.send_state.lift_state)
            werni_state = WerniState(message.data.send_state.werni_state)
            if lift_state == LiftState.LIFT_DOWN:
                _stop_run()
            logger.info('State - energy: %sWs, lift: %s, werni: %s', energy, lift_state, werni_state)
    except ValueError as error:
        logger.error('Failed to parse UART message: %s', error)
    except queue.Empty:
        pass


def _process_manager() -> None:
    """Checks if all processes are still alive."""
    # pylint: disable=possibly-used-before-assignment
    if not builder.halted() and not builder.alive():
        builder.start()
    if not stream_processing.halted() and not stream_processing.alive():
        stream_processing.start()

    if not uart_communicator.halted(reader=True) and not uart_communicator.alive(reader=True):
        uart_communicator.start(reader=True)
    if not uart_communicator.halted(writer=True) and not uart_communicator.alive(writer=True):
        uart_communicator.start(writer=True)


def _start_run() -> None:
    """Starts a new run."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Starting new run')
    while not builder_queue.empty() and not halt.is_set():
        builder_queue.get_nowait()
    while not uart_read.empty() and not halt.is_set():
        uart_read.get_nowait()
    while not uart_write.empty() and not halt.is_set():
        uart_write.get_nowait()

    time_measurement.reset()
    time_measurement.start()
    executor.submit(CubeApi.send_with_retry, api.post_start)
    uart_write.put(CommandBuilder.other_command(Command.PRIME_MAGAZINE))
    uart_write.put(CommandBuilder.other_command(Command.RESET_ENERGY_MEASUREMENT))
    builder.start()
    stream_processing.start_recognition()


def _stop_run() -> None:
    """Stops the run."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Stopping run')
    time_measurement.stop()
    stream_processing.stop_recognition()
    executor.submit(CubeApi.send_with_retry, api.post_end)
    logger.info('Run completed in %.3fs', time_measurement.total_runtime())


def _notify_systemd() -> None:
    """Notifies systemd that the app is started."""
    try:
        if 'NOTIFY_SOCKET' in os.environ:
            logger.info('Send ready signal to systemd')
            subprocess.run(['systemd-notify', f'--pid={os.getppid()}', '--ready'], capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        logger.error('Failed to notify systemd: %s', error.stderr.decode().strip())


def main() -> None:
    """The main application loop managing all processes."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Entering main loop')
    _notify_systemd()
    while not halt.is_set():
        _handle_uart_messages()
        _process_manager()

    logger.info('Exiting main loop')


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)
    logger = logging.getLogger('main')

    # Parse configuration file
    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    # Handle signals
    halt = Event()
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Initialize messaging queues
    builder_queue: Queue = Queue()
    uart_read: Queue = Queue()
    uart_write: Queue = Queue()

    # Initialize processes
    api = CubeApi(config)
    time_measurement = TimeMeasurement()
    executor = ProcessPoolExecutor(max_workers=2)
    builder = Builder(builder_queue, uart_write)
    stream_processing = StreamProcessing(config, builder_queue)
    uart_communicator = UartCommunicator(config, uart_read, uart_write)

    # Start initial processes
    stream_processing.start()
    uart_communicator.start(reader=True, writer=True)
    main()

    # Get config from web API
    api.send_with_retry(api.get_config)

    # Wait for processes to complete
    builder.join()
    stream_processing.join()
    uart_communicator.join(reader=True, writer=True)

    # Stop processes
    executor.shutdown()
    builder.stop()
    stream_processing.stop()
    uart_communicator.stop(reader=True, writer=True)
