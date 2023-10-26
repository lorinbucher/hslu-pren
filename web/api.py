"""Implements the APIs"""
import logging.config

import requests

import shared.config as app_config

SERVER_URL = 'http://18.192.48.168:5000'
TEAM_NR = '03'


class CubeApi:
    """The cube API"""

    def __init__(self):
        self._logger = logging.getLogger('web.cube_api')

    def get_availability(self) -> str:
        """Sends a GET request to the availability endpoint"""
        url = SERVER_URL + '/cubes'
        self._logger.info("send availability request: GET %s", url)
        try:
            response = requests.get(url=url, timeout=5)
            self._logger.info("availability response - status: %s, text: %s", response.status_code, response.text)
            return response.text
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return ""

    def post_cube_config(self, config: dict[str, str]) -> bool:
        """Sends a POST request to the cubes endpoint"""
        url = SERVER_URL + '/cubes/team' + TEAM_NR
        self._logger.info("send cube config request: POST %s %s", url, config)
        try:
            response = requests.post(url=url, json=config, timeout=5)
            self._logger.info("cube config response - status: %s, text: %s", response.status_code, response.text)
            return response.status_code % 100 == 2
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False


if __name__ == '__main__':
    logging.config.dictConfig(app_config.logging_config)

    cube_api = CubeApi()
    cube_api.get_availability()
    cube_api.post_cube_config({})
