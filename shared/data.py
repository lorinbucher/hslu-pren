"""Shared data classes"""
from dataclasses import dataclass


@dataclass()
class AppConfiguration:
    """The application configuration"""
    auth_team_nr: str = ''
    auth_token: str = ''
    server_api_address: str = ''

    def from_dict(self, data: dict) -> None:
        """Reads the app configuration from a dictionary"""
        self.auth_team_nr = data.get('auth', {}).get('team_nr', '')
        self.auth_token = data.get('auth', {}).get('token', '')
        self.server_api_address = data.get('server', {}).get('api_address', '')
