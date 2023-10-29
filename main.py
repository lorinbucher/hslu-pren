"""Main Application"""
import logging.config

import shared.config as app_config
from web.api import CubeApi

if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    cube_api = CubeApi(address="18.192.48.168:5000", team_nr="03")
    cube_api.get_availability()
    cube_api.post_cube_config({})
