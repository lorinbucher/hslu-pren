"""The main application of the 3D Re-Builder."""
import logging.config
import queue
import signal
import sys
import tomllib
from multiprocessing import Queue
from threading import Event

import shared.config as app_config
from builder.builder import Builder
from shared.data import AppConfiguration
from uart.command import Command
from uart.communicator import UartCommunicator
from video.manager import RecognitionManager

CONFIG_FILE = 'config.toml'


def _parse_config() -> dict:
    """Parses the configuration file."""
    logger = logging.getLogger('main.config')
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
    logger = logging.getLogger('main.config')
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
    if signum in (signal.SIGINT, signal.SIGTERM):
        uart_communicator.terminate_signal()
        recognition_manager.terminate_signal()
        builder.terminate_signal()
        terminate.set()


def _handle_uart_messages(terminate_signal: Event, recv_queue: Queue) -> None:
    """Handles received UART messages."""
    logger = logging.getLogger('main.messages')
    logger.info('Starting UART message listener')
    while not terminate_signal.is_set():
        try:
            message = recv_queue.get(timeout=2.0)
            logger.debug('Received UART message: %s', Command(message.cmd))
        except queue.Empty:
            continue

    logger.info('Stopping UART message listener')


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    # Parse configuration file
    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    # Handle signals
    terminate = Event()
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Initialize messaging queues
    builder_queue: Queue = Queue()
    uart_read: Queue = Queue()
    uart_write: Queue = Queue()

    # Initialize processes
    builder = Builder(builder_queue, uart_write)
    uart_communicator = UartCommunicator(config, uart_read, uart_write)
    recognition_manager = RecognitionManager(config, builder_queue)

    # Start processes
    uart_communicator.start()
    recognition_manager.start()
    builder.start()

    # TODO (lorin): start uart, video processing and web server from the beginning
    # TODO (lorin): start video recognition and builder after start signal received, reset in that case

    # Handle received UART messages
    _handle_uart_messages(terminate, uart_read)

    # Wait for processes to complete
    uart_communicator.join()
    recognition_manager.join()
    builder.join()

    # Stop processes
    uart_communicator.stop()
    recognition_manager.stop()
    builder.stop()
