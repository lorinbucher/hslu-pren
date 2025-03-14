"""Defines the commands used for the UART communication protocol."""
from _ctypes import Structure, Union
from ctypes import c_float, c_int16, c_uint8
from enum import Enum


class Command(Enum):
    """The build commands."""
    RESERVED = 0
    ACKNOWLEDGE = 1
    NOT_ACKNOWLEDGE = 2
    CRC_ERROR = 3
    ROTATE_GRID = 4
    PLACE_CUBES = 5
    MOVE_LIFT = 6
    GET_STATE = 7
    SEND_STATE = 8
    PAUSE_BUILD = 9
    RESUME_BUILD = 10
    PRIME_MAGAZINE = 11
    SEND_IO_STATE = 12
    EXECUTION_FINISHED = 13
    RESET_ENERGY_MEASUREMENT = 14
    RESET_WERNI = 15
    ENABLE_BUZZER = 16


class ButtonState(Enum):
    """The button states."""
    RELEASED = 0
    PRESSED = 1
    SHORT_CLICKED = 2
    LONG_CLICKED = 3


class LiftState(Enum):
    """The lift states."""
    UNHOMED = 0
    LIFT_UP = 1
    LIFT_DOWN = 2


class WerniState(Enum):
    """The WERNI states."""
    PREPARING = 0
    READY = 1
    BUILDING = 2
    BUILD_PAUSED = 3
    BUILD_ABORTED = 4


class RotateGrid(Structure):
    """The data payload of the rotate grid command."""
    _fields_ = [
        ('degrees', c_int16)
    ]


class PlaceCubes(Structure):
    """The data payload of the place cubes command."""
    _fields_ = [
        ('cubes_red', c_uint8),
        ('cubes_yellow', c_uint8),
        ('cubes_blue', c_uint8)
    ]


class MoveLift(Enum):
    """The data payload of the move lift command."""
    MOVE_UP = 0
    MOVE_DOWN = 1


class SendState(Structure):
    """The data payload of the send state command."""
    _fields_ = [
        ('energy', c_float),
        ('lift_state', c_uint8),
        ('werni_state', c_uint8)
    ]


class SendIOState(Structure):
    """The data payload of the send IO state command."""
    _fields_ = [
        ('btn_stop', c_uint8),
        ('btn_start', c_uint8)
    ]


class ExecFinished(Structure):
    """The data payload of the execution finished command."""
    _fields_ = [
        ('cmd', c_uint8),
        ('success', c_uint8)
    ]


class BuzzerState(Enum):
    """The data payload of the enable buzzer command."""
    DISABLE = 0
    ENABLE = 1


class DataUnion(Union):
    """The data payload for the UART message."""
    _fields_ = [
        ('rotate_grid', RotateGrid),
        ('place_cubes', PlaceCubes),
        ('move_lift', c_uint8),
        ('send_state', SendState),
        ('send_io_state', SendIOState),
        ('exec_finished', ExecFinished),
        ('enable_buzzer', c_uint8),
        ('data_field', c_uint8 * 16)
    ]


class Message(Structure):
    """The UART message."""
    _pack_ = 1
    _fields_ = [
        ('cmd', c_uint8),
        ('id', c_uint8),
        ('data', DataUnion),
        ('checksum', c_uint8)
    ]
