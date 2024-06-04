"""Shared data classes that are used in different parts of the application."""
from dataclasses import dataclass, field
from typing import Any

from shared.enumerations import CubeColor, Status


@dataclass
class AppConfiguration:
    """The configuration for the application."""
    api_address: str = 'oawz3wjih1.execute-api.eu-central-1.amazonaws.com'
    api_team_nr: str = '03'
    api_token: str = ''

    rtsp_address: str = '147.88.48.131'
    rtsp_user: str = 'pren'
    rtsp_password: str = ''
    rtsp_profile: str = 'pren_profile_med'

    serial_baud_rate: int = 115200
    serial_read: str = '/dev/ttyAMA0'
    serial_write: str = '/dev/ttyAMA0'

    app_efficiency_mode: bool = False
    app_fast_mode: bool = False
    app_incremental_build: bool = False
    app_confidence: int = 25
    app_recognition_timeout: int = 180

    def from_dict(self, data: dict) -> None:
        """Reads the app configuration from a dictionary."""
        self.api_address = data.get('api', {}).get('address', self.api_address)
        self.api_team_nr = data.get('api', {}).get('team_nr', self.api_team_nr)
        self.api_token = data.get('api', {}).get('token', self.api_token)

        self.rtsp_address = data.get('rtsp', {}).get('address', self.rtsp_address)
        self.rtsp_user = data.get('rtsp', {}).get('user', self.rtsp_user)
        self.rtsp_password = data.get('rtsp', {}).get('password', self.rtsp_password)
        self.rtsp_profile = data.get('rtsp', {}).get('profile', self.rtsp_profile)

        self.serial_baud_rate = data.get('serial', {}).get('baud_rate', self.serial_baud_rate)
        self.serial_read = data.get('serial', {}).get('read', self.serial_read)
        self.serial_write = data.get('serial', {}).get('write', self.serial_write)

        self.app_efficiency_mode = data.get('app', {}).get('efficiency_mode', self.app_efficiency_mode)
        self.app_fast_mode = data.get('app', {}).get('fast_mode', self.app_fast_mode)
        self.app_incremental_build = data.get('app', {}).get('incremental_build', self.app_incremental_build)
        self.app_confidence = data.get('app', {}).get('confidence', self.app_confidence)
        self.app_recognition_timeout = data.get('app', {}).get('recognition_timeout', self.app_recognition_timeout)

    def to_dict(self) -> dict[str, Any]:
        """Converts the app configuration to a dictionary."""
        return {
            'app': {
                'efficiency_mode': self.app_efficiency_mode,
                'fast_mode': self.app_fast_mode,
                'incremental_build': self.app_incremental_build,
                'confidence': self.app_confidence,
                'recognition_timeout': self.app_recognition_timeout
            },
            'api': {
                'address': self.api_address,
                'team_nr': self.api_team_nr,
                'token': self.api_token
            },
            'rtsp': {
                'address': self.rtsp_address,
                'user': self.rtsp_user,
                'password': self.rtsp_password,
                'profile': self.rtsp_profile
            },
            'serial': {
                'baud_rate': self.serial_baud_rate,
                'read': self.serial_read,
                'write': self.serial_write
            },
        }

    def validate(self) -> tuple[bool, str]:
        """Validates the configuration of the application."""
        for key, value in self.__dict__.items():
            if key in ('app_confidence', 'app_recognition_timeout', 'serial_baud_rate'):
                result = isinstance(value, int) and value > 0
            elif key in ('app_incremental_build', 'app_efficiency_mode', 'app_fast_mode'):
                result = isinstance(value, bool)
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
    config: list[CubeColor] = field(default_factory=lambda: [CubeColor.UNKNOWN for _ in range(8)])

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

    def set_color(self, color: CubeColor, pos: int, offset: int = 0) -> None:
        """Sets the color at the specified position with an optional offset.
        Position starts at 1. Offsets are applied separately to the lower (1-4)
        and upper (5-8) positions in a rolling manner.
        """
        if pos < 1 or pos > 8:
            return
        start_index = 4 if pos > 4 else 0
        rolled_pos = (pos - 1 - start_index + offset) % 4
        self.config[rolled_pos + start_index] = color

    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary containing the cube configuration."""
        data = {}
        for index, value in enumerate(self.config):
            data[str(index + 1)] = str(value)
        return data

    def set_default(self) -> None:
        """Sets the default configuration used if the cube image recognition fails."""
        self.config = [
            CubeColor.RED, CubeColor.BLUE, CubeColor.YELLOW, CubeColor.BLUE,
            CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE
        ]


@dataclass
class StatusData:
    """Holds the status of the 3D Re-Builder application."""
    config: list[CubeColor] = field(default_factory=lambda: [CubeColor.UNKNOWN for _ in range(8)])
    energy: float = 0.0
    status: Status = Status.IDLE
    steps_finished: int = 0
    steps_total: int = 0
    time_config: int = 0
    time_end: int = 0
    time_start: int = 0

    def reset(self) -> None:
        """Resets the status."""
        self.config = [CubeColor.UNKNOWN for _ in range(8)]
        self.energy = 0.0
        self.status = Status.IDLE
        self.steps_finished = 0
        self.steps_total = 0
        self.time_config = 0
        self.time_end = 0
        self.time_start = 0

    @property
    def duration_config(self) -> float:
        """Returns the duration until the configuration was detected."""
        return (self.time_config - self.time_start) / 1_000_000_000

    @property
    def duration_total(self) -> float:
        """Returns the total duration for the run."""
        return (self.time_end - self.time_start) / 1_000_000_000
