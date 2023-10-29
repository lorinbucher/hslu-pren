"""Shared data classes"""
from dataclasses import dataclass, fields

from shared.enum import CubeColor


@dataclass
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


@dataclass
class CubeConfiguration:
    """The cube configuration"""
    # pylint: disable=too-many-instance-attributes
    pos1: CubeColor = CubeColor.NONE
    pos2: CubeColor = CubeColor.NONE
    pos3: CubeColor = CubeColor.NONE
    pos4: CubeColor = CubeColor.NONE
    pos5: CubeColor = CubeColor.NONE
    pos6: CubeColor = CubeColor.NONE
    pos7: CubeColor = CubeColor.NONE
    pos8: CubeColor = CubeColor.NONE

    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary containing the cube configuration"""
        data = {}
        for field in fields(self):
            data[field.name.removeprefix('pos')] = str(getattr(self, field.name))
        return data
