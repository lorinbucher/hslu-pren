"""Main Application"""
import logging.config
import sys
import time
import tomllib

import shared.config as app_config
from shared.data import AppConfiguration, CubeConfiguration
from shared.enumerations import CubeColor
from web.api import CubeApi


def _parse_config() -> dict:
    """Parses the configuration file"""
    logger = logging.getLogger('main.config')
    try:
        with open('config.toml', 'rb') as config_file:
            return tomllib.load(config_file)
    except (FileNotFoundError, PermissionError) as error:
        logger.error('Failed to read config.toml file: %s', error)
    except tomllib.TOMLDecodeError as error:
        logger.error('Failed to parse config.toml file: %s', error)
    sys.exit(1)


def _validate_config(conf: AppConfiguration) -> None:
    """Validates the configuration"""
    logger = logging.getLogger('main.config')
    is_valid, error = conf.validate()
    if not is_valid:
        logger.error('Invalid configuration: %s', error)
        sys.exit(1)


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    cube_api = CubeApi(config)
    if cube_api.get_availability():
        cube_config = CubeConfiguration()
        cube_config.pos2 = CubeColor.BLUE
        cube_config.pos4 = CubeColor.RED
        cube_config.pos6 = CubeColor.YELLOW
        cube_config.pos8 = CubeColor.NONE

        cube_api.post_start()
        time.sleep(5)
        cube_api.post_config(cube_config)
        time.sleep(2)
        cube_api.post_end()
        cube_api.get_config()
