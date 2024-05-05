"""The main application of the 3D Re-Builder."""
import logging.config
import sys
import tomllib
from multiprocessing import Pipe

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


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    # TODO (lorin): start builder task
    # TODO (lorin): start recognition manager
    # TODO (lorin): start web server to serve the user interface
    # TODO (lorin): start UART listener task

    # TODO (lorin): on start signal received, flush processing queue or not depending on rules, send request
    # TODO (lorin): on sube detected, send configuration to builder task
    # TODO (lorin): on detection finished, stop recognition task, send config request (maybe from video.manager)

    config_conn_recv, config_conn_send = Pipe(duplex=False)
    recognition_manager = RecognitionManager(config, config_conn_send)
    recognition_manager.clear_queue()
    recognition_manager.start()
    recognition_manager.join()
