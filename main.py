"""The main application of the 3D Re-Builder."""
import logging.config
import multiprocessing
import queue
import signal
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
from threading import Event

import shared.config as app_config
from builder.builder import Builder
from measure import TimeMeasurement
from shared.data import AppConfiguration
from uart.command import Command
from uart.commandbuilder import CommandBuilder
from uart.communicator import UartCommunicator
from video.manager import RecognitionManager
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
        uart_communicator.halt(reader=True, writer=True)
        recognition_manager.halt(processing=True, recognition=True)
        builder.halt()
        halt.set()


def _handle_uart_messages() -> None:
    """Handles received UART messages."""
    # pylint: disable=possibly-used-before-assignment
    try:
        message = uart_read.get(timeout=0.25)
        cmd = Command(message.cmd)
        logger.debug('Received UART message: %s', cmd)

        if cmd == Command.SEND_STATE:  # TODO (lorin): implement actual command
            _start_run()
    except queue.Empty:
        pass


def _process_manager() -> None:
    """Checks if all processes are still alive."""
    # pylint: disable=possibly-used-before-assignment
    if not builder.halted() and not builder.alive():
        builder.start()

    if not recognition_manager.halted(processing=True) and not recognition_manager.alive(processing=True):
        recognition_manager.start(processing=True)
    if not recognition_manager.halted(recognition=True) and not recognition_manager.alive(recognition=True):
        recognition_manager.start(recognition=True)

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
    builder.start()
    recognition_manager.start(recognition=True)


def _stop_run() -> None:
    """Stops the run."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Stopping run')
    time_measurement.stop()
    executor.submit(CubeApi.send_with_retry, api.post_end)
    logger.info('Run completed in %.3fs', time_measurement.total_runtime())


def main() -> None:
    """The main application loop managing all processes."""
    # pylint: disable=possibly-used-before-assignment
    logger.info('Entering main loop')
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
    executor = ProcessPoolExecutor()
    builder = Builder(builder_queue, uart_write)
    recognition_manager = RecognitionManager(config, builder_queue)
    uart_communicator = UartCommunicator(config, uart_read, uart_write)

    # Start initial processes
    uart_communicator.start(reader=True, writer=True)
    recognition_manager.start(processing=True)
    main()

    # TODO (lorin): implement actual handling of end
    _stop_run()
    api.send_with_retry(api.get_config)

    # Wait for processes to complete
    builder.join()
    recognition_manager.join(processing=True, recognition=True)
    uart_communicator.join(reader=True, writer=True)

    # Stop processes
    executor.shutdown()
    builder.stop()
    recognition_manager.stop(processing=True, recognition=True)
    uart_communicator.stop(reader=True, writer=True)
