"""The main of the 3D Re-Builder application."""
import logging.config
import multiprocessing
import os
import signal
import subprocess
import sys
import tomllib
from threading import Event

import shared.config as app_config
from rebuilder.app import RebuilderApplication
from shared.data import AppConfiguration

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
        rebuilder_app.halt()


def _notify_systemd() -> None:
    """Notifies systemd that the app is started."""
    try:
        if 'NOTIFY_SOCKET' in os.environ:
            logger.info('Send ready signal to systemd')
            subprocess.run(['systemd-notify', f'--pid={os.getpid()}', '--ready'], capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        logger.error('Failed to notify systemd: %s', error.stderr.decode().strip())


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
    _notify_systemd()

    # Run application
    rebuilder_app = RebuilderApplication(config)
    rebuilder_app.start()
    rebuilder_app.run()
    rebuilder_app.join()
    rebuilder_app.stop()
