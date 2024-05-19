"""Implements the cube image recognition module."""
from typing import Any

from shared.data import CubeConfiguration
from shared.enumerations import CubeColor

FRAME_CROP_X = 400
FRAME_CROP_Y = 0
FRAME_CROP_W = 500
FRAME_CROP_H = 400


class CubeRecognition:
    """Provides functions to run the cube image recognition."""

    def __init__(self):
        pass

    @staticmethod
    def crop_frame(frame: Any) -> Any:
        """Crops the frame to the region of interest to reduce processing load."""
        if frame is not None:
            return frame[FRAME_CROP_Y:FRAME_CROP_Y + FRAME_CROP_H, FRAME_CROP_X:FRAME_CROP_X + FRAME_CROP_W]
        return None

    @staticmethod
    def process_frame(frame: Any) -> list[CubeColor]:
        """Performs the cube image recognition on a single frame."""
        config = CubeConfiguration()
        if frame is not None:
            config.set_color(1, CubeColor.BLUE)
            config.set_color(2, CubeColor.RED)
            config.set_color(3, CubeColor.YELLOW)
            config.set_color(4, CubeColor.NONE)
            config.set_color(5, CubeColor.BLUE)
            config.set_color(6, CubeColor.RED)
            config.set_color(7, CubeColor.YELLOW)
            config.set_color(8, CubeColor.NONE)
        return config.config
