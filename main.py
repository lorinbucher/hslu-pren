"""The main application of the 3D Re-Builder."""
import logging.config
import signal
import sys
import tomllib
from multiprocessing import SimpleQueue

import shared.config as app_config
from shared.data import AppConfiguration
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
        recognition_manager.terminate_signal()


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    # Parse configuration file
    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    # Handle signals
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # uart_read = SimpleQueue()
    # uart_write = SimpleQueue()
    # uart_communicator = UartCommunicator(config, uart_read, uart_write)

    builder_queue: SimpleQueue = SimpleQueue()
    recognition_manager = RecognitionManager(config, builder_queue)
    recognition_manager.start()
    recognition_manager.join()
    recognition_manager.stop()

    # Temporary for testing
    data = builder_queue.get()
    logging.info('Detected cube configuration: %s', data.to_dict())
