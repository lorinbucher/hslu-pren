from enum import Enum
from ctypes import *


# Hier ich habe die Config von der Elektronik so nach python geschrieben
class COMMAND(Enum):
    CMD_RESERVED = 0
    CMD_ACKNOWLEDGE = 1
    CMD_NOT_ACKNOWLEDGE = 2
    CMD_CRC_ERROR = 3
    CMD_ROTATE_GRID = 4
    CMD_PLACE_CUBES = 5
    CMD_MOVE_LIFT = 6
    CMD_GET_STATE = 7
    CMD_SEND_STATE = 8
    CMD_PAUSE_BUILD = 9
    CMD_RESUME_BUILD = 10


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
