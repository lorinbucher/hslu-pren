"""The shared logging configuration that should be used in all parts of the application."""
import json
import logging
import sys
from typing import Any

CONFIG_FILE = 'config.json'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(name)-25s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'stderr': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stderr,
        },
    },
    'loggers': {
        'urllib3': {'level': 'INFO', },
        'werkzeug': {'level': 'ERROR', },
    },
    'root': {
        'handlers': ['stdout', ],
        'level': 'DEBUG',
    },
}


def read_config_file() -> dict[str, Any]:
    """Parses the configuration file."""
    logger = logging.getLogger('config')
    try:
        logger.info('Parsing configuration file: %s', CONFIG_FILE)
        with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except (FileNotFoundError, PermissionError) as error:
        logger.error('Failed to read %s file: %s', CONFIG_FILE, error)
    except json.JSONDecodeError as error:
        logger.error('Failed to parse %s file: %s', CONFIG_FILE, error)
    return {}


def write_config_file(config: dict[str, Any]) -> None:
    """Writes the configuration file."""
    logger = logging.getLogger('config')
    try:
        logger.info('Writing configuration file: %s', CONFIG_FILE)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, indent=2)
    except (FileNotFoundError, PermissionError) as error:
        logger.error('Failed to write %s file: %s', CONFIG_FILE, error)
    except json.JSONDecodeError as error:
        logger.error('Failed to parse data: %s', error)
