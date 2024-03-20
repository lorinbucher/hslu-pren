"""Implements the APIs"""
import logging.config
from datetime import datetime

import requests

from shared.data import AppConfiguration, CubeConfiguration


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

    def get_config(self) -> bool:
        """Sends a GET request to receive the recognized cube configuration"""
        url = 'http://' + self._address + '/cubes/team' + self._team_nr
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info("send cube config request: GET %s", url)
        try:
            response = requests.get(url=url, headers=headers, timeout=5)
            self._logger.info("cube config response - status: %s, text: %s", response.status_code, response.json())
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False

    def post_start(self) -> bool:
        """Sends a POST request to start a new run"""
        url = 'http://' + self._address + '/cubes/team' + self._team_nr + "/start"
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info("send start request: POST %s", url)
        try:
            response = requests.post(url=url, headers=headers, timeout=5)
            self._logger.info("start response - status: %s, text: %s", response.status_code, response.text)
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False

    def post_config(self, cube_config: CubeConfiguration) -> bool:
        """Sends a POST request with the recognized cube configuration"""
        json_data = self._create_cube_config_payload(cube_config)
        url = 'http://' + self._address + '/cubes/team' + self._team_nr + "/config"
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info("send cube config request: POST %s %s", url, json_data)
        try:
            response = requests.post(url=url, headers=headers, json=json_data, timeout=5)
            self._logger.info("cube config response - status: %s, text: %s", response.status_code, response.text)
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False

    def post_end(self) -> bool:
        """Sends a POST request to end the current run"""
        url = 'http://' + self._address + '/cubes/team' + self._team_nr + "/end"
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info("send end request: POST %s", url)
        try:
            response = requests.post(url=url, headers=headers, timeout=5)
            self._logger.info("end response - status: %s, text: %s", response.status_code, response.text)
            return 200 <= response.status_code <= 299
        except requests.exceptions.RequestException as error:
            self._logger.error("request failed: %s", error)
            return False

    @staticmethod
    def _create_cube_config_payload(cube_config: CubeConfiguration) -> dict:
        """Creates the JSON payload for the post request of the cube configuration"""
        return {
            'time': datetime.utcnow().isoformat(),
            'config': cube_config.to_dict()
        }
