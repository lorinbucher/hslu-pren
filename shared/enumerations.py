"""Shared enumerations that are used in different parts of the application."""
from enum import StrEnum


class CubeColor(StrEnum):
    """The colors a cube in the configuration can have.

    UNKNOWN means it's not clear yet, if the space is empty or not.
    NONE means there is no cube at that position and therefore the space is empty.
    """
    UNKNOWN = 'unknown'
    NONE = ''
    BLUE = 'blue'
    RED = 'red'
    YELLOW = 'yellow'
