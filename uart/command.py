"""Defines the commands used for the UART communication protocol."""
from _ctypes import Structure, Union
from ctypes import c_int16, c_uint8
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
        ('dummy1', c_uint8),
        ('dummy2', c_uint8),
        ('dummy3', c_uint8),
        ('dummy4', c_uint8)
    ]


class SendIOState(Structure):
    """The data payload of the send IO state command."""
    _fields_ = [
        ('btn_start', c_uint8),
        ('btn_stop', c_uint8)
    ]


class DataUnion(Union):
    """The data payload for the UART message."""
    _fields_ = [
        ('rotate_grid', RotateGrid),
        ('place_cubes', PlaceCubes),
        ('move_lift', c_uint8),
        ('send_state', SendState),
        ('send_io_state', SendIOState),
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
