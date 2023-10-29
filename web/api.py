"""Implements the APIs"""
import logging.config

import requests


class CubeApi:
    """The cube API"""

    def __init__(self, address: str, team_nr: str):
        self._logger = logging.getLogger('web.cube_api')
        self._address = address
        self._team_nr = team_nr

    def get_availability(self) -> str:
        """Sends a GET request to the availability endpoint"""
        url = 'http://' + self._address + '/cubes'
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
        url = 'http://' + self._address + '/cubes/team' + self._team_nr
        self._logger.info("send cube config request: POST %s %s", url, config)
        try:
            response = requests.post(url=url, json=config, timeout=5)
            self._logger.info("cube config response - status: %s, text: %s", response.status_code, response.text)
            return response.status_code % 100 == 2
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False
