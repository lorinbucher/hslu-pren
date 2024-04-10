from enum import Enum
from ctypes import *


# Hier ich habe die Config von der Elektronik so nach python geschrieben
class COMMAND(Enum):
    CMD_RESERVED = 0
    CMD_ACKNOWLEDGE = 1
    CMD_NOT_ACKNOWLEDGE = 2
    CMD_ROTATE_GRID = 3
    CMD_PLACE_CUBES = 4
    CMD_MOVE_LIFT = 5
    CMD_STATE = 6


class CmdRotateGrid(Structure):
    _fields_ = [("degrees_h", c_uint8),
                ("degrees_l", c_uint8)]


class CmdPlaceCubes(Structure):
    _fields_ = [("cubes_red", c_uint8),
                ("cubes_yellow", c_uint8),
                ("cubes_blue", c_uint8)]


class CmdMoveLift(Enum):
    MOVE_UP = 0
    MOVE_DOWN = 1


class DataUnion(Union):
    _fields_ = [("cmdRotateGrid", CmdRotateGrid),
                ("cmdPlaceCubes", CmdPlaceCubes),
                ("cmdMoveLift", c_uint8),
                ("dataField", c_uint8 * 16)]


class Message(Structure):
    _fields_ = [("cmd", c_uint8),
                ("dataUnion", DataUnion),
                ("checksum", c_uint8)]
