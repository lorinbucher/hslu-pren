"""Main Application"""
import logging.config
import sys
import tomllib

import shared.config as app_config
from shared.data import AppConfiguration
from web.api import CubeApi


def _parse_config() -> dict:
    """Parses the configuration file"""
    logger = logging.getLogger('main.config')
    try:
        with open('config.toml', 'rb') as config_file:
            return tomllib.load(config_file)
    except (FileNotFoundError, PermissionError) as error:
        logger.error("failed to read config.toml file: %s", error)
    except tomllib.TOMLDecodeError as error:
        logger.error("failed to parse config.toml file: %s", error)
    sys.exit(1)


def _validate_config(conf: AppConfiguration) -> None:
    """Validates the configuration"""
    logger = logging.getLogger('main.config')
    valid = True
    if not conf.auth_team_nr or not isinstance(conf.auth_team_nr, str):
        logger.error("invalid configuration: auth.team_nr must be a non-empty string")
        valid = False
    if not conf.auth_token or not isinstance(conf.auth_token, str):
        logger.error("invalid configuration: auth.auth_token must be a non-empty string")
        valid = False
    if not conf.server_api_address or not isinstance(conf.server_api_address, str):
        logger.error("invalid configuration: server.api_address must be a non-empty string")
        valid = False
    if not valid:
        sys.exit(1)


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    config = AppConfiguration()
    config.from_dict(_parse_config())
    _validate_config(config)

    cube_api = CubeApi(config)
    cube_api.get_availability()
    cube_api.post_cube_config({})
