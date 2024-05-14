"""The main application of the 3D Re-Builder."""
import logging.config
import signal
import sys
import tomllib
from multiprocessing import Queue

import shared.config as app_config
from builder.builder import Builder
from shared.data import AppConfiguration
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


def _signal_handler(signum, _):
    """Handles signals to gracefully stop the application."""
    if signum in (signal.SIGINT, signal.SIGTERM):
        uart_communicator.terminate_signal()
        recognition_manager.terminate_signal()
        builder.terminate_signal()


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    # Parse configuration file
    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    # Handle signals
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
    # TODO (lorin): handle received uart messages

    # Wait for processes to complete
    uart_communicator.join()
    recognition_manager.join()
    builder.join()

    # Stop processes
    uart_communicator.stop()
    recognition_manager.stop()
    builder.stop()
