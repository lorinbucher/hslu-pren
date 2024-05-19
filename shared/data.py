"""Shared data classes that are used in different parts of the application."""
from dataclasses import dataclass

from shared.enumerations import CubeColor


@dataclass
class AppConfiguration:
    """The configuration for the application."""
    auth_team_nr: str = ''
    auth_token: str = ''

    server_api_address: str = ''
    server_rtsp_address: str = ''

    rtsp_user: str = ''
    rtsp_password: str = ''
    rtsp_profile: str = ''

    app_confidence: int = 0
    serial_read: str = ''
    serial_write: str = ''

    def from_dict(self, data: dict) -> None:
        """Reads the app configuration from a dictionary."""
        self.auth_team_nr = data.get('auth', {}).get('team_nr', '')
        self.auth_token = data.get('auth', {}).get('token', '')

        self.server_api_address = data.get('server', {}).get('api_address', '')
        self.server_rtsp_address = data.get('server', {}).get('rtsp_address', '')

        self.rtsp_user = data.get('rtsp', {}).get('user', '')
        self.rtsp_password = data.get('rtsp', {}).get('password', '')
        self.rtsp_profile = data.get('rtsp', {}).get('profile', '')

        self.app_confidence = data.get('app', {}).get('confidence', 0)
        self.serial_read = data.get('app', {}).get('serial_read', '')
        self.serial_write = data.get('app', {}).get('serial_write', '')

    def validate(self) -> tuple[bool, str]:
        """Validates the configuration of the application."""
        for key, value in self.__dict__.items():
            if key == 'app_confidence':
                result = isinstance(value, int) and value > 0
            else:
                result = isinstance(value, str) and bool(value.strip())

            if not result:
                return False, key.replace('_', '.', 1)
        return True, ''


@dataclass
class CubeConfiguration:
    """The positions of a cube or an empty space in the configuration.

    Values 1-8 denote the positions of a cube or an empty space in the configuration.
    Position 1 specifies the point that lies on the reference sector of the turntable,
    positions 2-4 specify sectors on the turntable in the counterclockwise direction.
    The Positions 5-8 are those on the 2nd level, on top of the underlying cube.
    """
    config = [CubeColor.UNKNOWN for _ in range(8)]

    def completed(self) -> bool:
        """Returns true if all positions are known."""
        return CubeColor.UNKNOWN not in self.config

    def reset(self) -> None:
        """Resets the configuration."""
        self.config = [CubeColor.UNKNOWN for _ in range(8)]

    def get_color(self, pos: int) -> CubeColor:
        """Gets the color at the specified position, position starts at 1."""
        if pos < 1 or pos > 8:
            return CubeColor.UNKNOWN
        return self.config[pos - 1]

    def set_color(self, pos: int, color: CubeColor) -> None:
        """Sets the color at the specified position, position starts at 1."""
        if pos < 1 or pos > 8:
            return
        self.config[pos - 1] = color

    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary containing the cube configuration."""
        data = {}
        for index, value in enumerate(self.config):
            data[str(index + 1)] = str(value)
        return data
