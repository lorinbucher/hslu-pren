"""Implements the APIs"""
import logging.config

import requests

from shared.data import AppConfiguration


class CubeApi:
    """The cube API"""

    def __init__(self, app_config: AppConfiguration):
        self._logger = logging.getLogger('web.cube_api')
        self._address = app_config.server_api_address
        self._team_nr = app_config.auth_team_nr
        self._auth_token = app_config.auth_token

    def get_availability(self) -> bool:
        """Sends a GET request to the availability endpoint"""
        url = 'http://' + self._address + '/cubes'
        self._logger.info("send availability request: GET %s", url)
        try:
            response = requests.get(url=url, timeout=5)
            self._logger.info("availability response - status: %s, text: %s", response.status_code, response.text)
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False

    def post_cube_config(self, cube_config: dict[str, str]) -> bool:
        """Sends a POST request to the cubes endpoint"""
        url = 'http://' + self._address + '/cubes/team' + self._team_nr
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self._auth_token}'}
        self._logger.info("send cube config request: POST %s %s", url, cube_config)
        try:
            response = requests.post(url=url, headers=headers, json=cube_config, timeout=5)
            self._logger.info("cube config response - status: %s, text: %s", response.status_code, response.json())
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False
