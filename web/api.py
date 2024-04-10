"""Implements the Cube API."""
import logging.config
from datetime import datetime
from typing import Any

import requests

from shared.data import AppConfiguration, CubeConfiguration


class CubeApi:
    """Provides functions to interact with the Cube API."""

    def __init__(self, app_config: AppConfiguration):
        self._logger = logging.getLogger('web.cube_api')
        self._address = app_config.server_api_address
        self._team_nr = app_config.auth_team_nr
        self._auth_token = app_config.auth_token

    def get_availability(self) -> bool:
        """Sends a GET request to the availability endpoint."""
        self._logger.info('Sending availability request')
        response = self._get_request(f'https://{self._address}/cubes')
        return 200 <= response.status_code <= 299 if response else False

    def get_config(self) -> bool:
        """Sends a GET request to receive the recognized cube configuration."""
        self._logger.info('Sending cube config request')
        response = self._get_request(f'https://{self._address}/cubes/team{self._team_nr}')
        return 200 <= response.status_code <= 299 if response else False

    def post_start(self) -> bool:
        """Sends a POST request to start a new run."""
        self._logger.info('Sending start request')
        response = self._post_request(f'https://{self._address}/cubes/team{self._team_nr}/start')
        return 200 <= response.status_code <= 299 if response else False

    def post_config(self, cube_config: CubeConfiguration) -> bool:
        """Sends a POST request with the recognized cube configuration."""
        self._logger.info('Sending config request')
        data = {
            'time': datetime.utcnow().isoformat(),
            'config': cube_config.to_dict()
        }
        response = self._post_request(f'https://{self._address}/cubes/team{self._team_nr}/config', data=data)
        return 200 <= response.status_code <= 299 if response else False

    def post_end(self) -> bool:
        """Sends a POST request to end the current run."""
        self._logger.info('Sending end request')
        response = self._post_request(f'https://{self._address}/cubes/team{self._team_nr}/end')
        return 200 <= response.status_code <= 299 if response else False

    def _get_request(self, url: str) -> requests.Response | None:
        """Sends a GET request to the specified URL."""
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info('GET request: %s', url)
        try:
            response = requests.get(url=url, headers=headers, timeout=5)
            self._logger.info('GET response: status=%s, data=%s', response.status_code, self._parse_data(response))
            return response
        except requests.exceptions.RequestException as error:
            self._logger.error('Request failed: url=%s, error=%s', url, error)
            return None

    def _post_request(self, url: str, data: dict[str, Any] | None = None) -> requests.Response | None:
        """Sends a POST request to the specified URL."""
        headers = {'Auth': f'{self._auth_token}'}
        self._logger.info('POST request: %s data=%s', url, data)
        try:
            response = requests.post(url=url, headers=headers, json=data, timeout=5)
            self._logger.info('POST response: status=%s, data=%s', response.status_code, self._parse_data(response))
            return response
        except requests.exceptions.RequestException as error:
            self._logger.error('Request failed: url=%s, error=%s', url, error)
            return None

    @staticmethod
    def _parse_data(response: requests.Response) -> str | dict[str, Any]:
        """Parses the data of the response."""
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text
