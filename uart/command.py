from _ctypes import Structure, Union
from ctypes import c_int16, c_uint8
from enum import Enum


class Command(Enum):
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


class CmdRotateGrid(Structure):
    _fields_ = [("degrees", c_int16)]


class CmdPlaceCubes(Structure):
    _fields_ = [("cubes_red", c_uint8),
                ("cubes_yellow", c_uint8),
                ("cubes_blue", c_uint8)]


class CmdMoveLift(Enum):
    MOVE_UP = 0
    MOVE_DOWN = 1


class CmdSendState(Structure):
    _fields_ = [("dummy1", c_uint8),
                ("dummy2", c_uint8),
                ("dummy3", c_uint8),
                ("dummy4", c_uint8)]


class DataUnion(Union):
    _fields_ = [("cmdRotateGrid", CmdRotateGrid),
                ("cmdPlaceCubes", CmdPlaceCubes),
                ("cmdMoveLift", c_uint8),
                ("cmdSendState", CmdSendState),
                ("dataField", c_uint8 * 16)]


class Message(Structure):
    _fields_ = [("cmd", c_uint8),
                ("id", c_uint8),
                ("dataUnion", DataUnion),
                ("checksum", c_uint8)]
