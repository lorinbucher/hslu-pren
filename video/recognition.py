"""Implements the cube image recognition module."""
from typing import Any

import cv2
import numpy as np

from shared.data import CubeConfiguration
from shared.enumerations import CubeColor

# Frame region of interest
FRAME_CROP_X = 375
FRAME_CROP_Y = 25
FRAME_CROP_W = 500
FRAME_CROP_H = 400

# Color ranges
# TODO (lorin): tweak ranges more, to optimize detection and remove noise
LOWER_REF = np.array([0, 0, 175])
UPPER_REF = np.array([180, 60, 255])
LOWER_BLUE = np.array([100, 100, 75])
UPPER_BLUE = np.array([130, 255, 255])
LOWER_RED_LOW = np.array([0, 75, 50])
UPPER_RED_LOW = np.array([10, 255, 255])
LOWER_RED_HIGH = np.array([160, 75, 50])
UPPER_RED_HIGH = np.array([180, 255, 255])
LOWER_YELLOW = np.array([20, 75, 50])
UPPER_YELLOW = np.array([40, 255, 255])


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
        if frame is None:
            return config.config

        # Color Segmentation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_ref = cv2.inRange(hsv, LOWER_REF, UPPER_REF)
        mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
        mask_red_low = cv2.inRange(hsv, LOWER_RED_LOW, UPPER_RED_LOW)
        mask_red_high = cv2.inRange(hsv, LOWER_RED_HIGH, UPPER_RED_HIGH)
        mask_red = cv2.bitwise_or(mask_red_low, mask_red_high)
        mask_yellow = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
        mask_cube = cv2.bitwise_or(mask_blue, mask_red)
        mask_cube = cv2.bitwise_or(mask_cube, mask_yellow)
        mask_cube = cv2.morphologyEx(mask_cube, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))

        # Contour Detection
        contours_cube = CubeRecognition._contour_with_min_size(mask_cube, 2500)
        contours_ref = CubeRecognition._contour_with_min_size(mask_ref, 2500)
        contours_blue = CubeRecognition._contour_with_min_size(mask_blue)
        contours_red = CubeRecognition._contour_with_min_size(mask_red)
        contours_yellow = CubeRecognition._contour_with_min_size(mask_yellow)
        if not contours_cube or not contours_ref:
            return config.config

        # Filter contours that are not near the detected cube
        contour_cube = max(contours_cube, key=lambda c: cv2.contourArea(c))  # pylint: disable=unnecessary-lambda
        # contour_ref = max(contours_ref, key=lambda c: cv2.contourArea(c))  # pylint: disable=unnecessary-lambda
        contour_map = ([(CubeColor.BLUE, c, CubeRecognition._contour_center(c)) for c in contours_blue] +
                       [(CubeColor.RED, c, CubeRecognition._contour_center(c)) for c in contours_red] +
                       [(CubeColor.YELLOW, c, CubeRecognition._contour_center(c)) for c in contours_yellow])
        contour_map = [cnt for cnt in contour_map if CubeRecognition._point_in_contour(contour_cube, cnt[2])]

        offset = CubeRecognition._reference_offset(contours_ref, FRAME_CROP_W, FRAME_CROP_H)
        if offset >= 0 and len(contour_map) > 0:
            config.set_color(CubeRecognition._find_color_for_point(contour_map, None, (200, 300)), 1, offset)
            config.set_color(CubeRecognition._find_color_for_point(contour_map, None, (300, 300)), 2, offset)
            config.set_color(CubeRecognition._find_color_for_point(contour_map, None, (300, 80)), 7, offset)
            config.set_color(CubeRecognition._find_color_for_point(contour_map, None, (200, 80)), 8, offset)
        return config.config

    @staticmethod
    def _contour_center(contour: Any) -> tuple[int, int]:
        """Returns the center of the contour."""
        moments = cv2.moments(contour)
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
        return x, y

    # TODO (lorin): tweak size to recognize small parts of a cube
    @staticmethod
    def _contour_with_min_size(source: Any, size: int = 100):
        """Finds contours that have the given minimum size."""
        # Retrieval external because there are no nested contours
        contours, _ = cv2.findContours(source, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [contour for contour in contours if cv2.contourArea(contour) > size]

    @staticmethod
    def _point_distance(contour: Any, point: tuple[float, float]):
        """Returns the distance between the contour and the point."""
        return cv2.pointPolygonTest(contour, point, measureDist=True)

    @staticmethod
    def _point_in_contour(contour: Any, point: tuple[float, float]):
        """Returns true if the point is within the contour."""
        return cv2.pointPolygonTest(contour, point, measureDist=False) >= 0

    @staticmethod
    def _point_in_any_contour(contours: list[Any], point: tuple[float, float]):
        """Returns true if the point is within any of the contours."""
        return any(CubeRecognition._point_in_contour(cnt, point) for cnt in contours)

    @staticmethod
    def _reference_offset(refs: list[Any], width: int, height: int) -> int:
        """Returns the reference offset, negative if not entirely clear."""
        count = 0
        offset = -1
        if (CubeRecognition._point_in_any_contour(refs, (25, height - 25)) and
                CubeRecognition._point_in_any_contour(refs, (25, height - 100)) and
                CubeRecognition._point_in_any_contour(refs, (200, height - 25))):
            count += 1
            offset = 0
        if (CubeRecognition._point_in_any_contour(refs, (25, height - 175)) and
                CubeRecognition._point_in_any_contour(refs, (75, 150)) and
                CubeRecognition._point_in_any_contour(refs, (125, 125))):
            count += 1
            offset = 1
        if (CubeRecognition._point_in_any_contour(refs, (width - 25, height - 175)) and
                CubeRecognition._point_in_any_contour(refs, (width - 75, 150)) and
                CubeRecognition._point_in_any_contour(refs, (width - 125, 125))):
            count += 1
            offset = 2
        if (CubeRecognition._point_in_any_contour(refs, (width - 25, height - 25)) and
                CubeRecognition._point_in_any_contour(refs, (width - 25, height - 100)) and
                CubeRecognition._point_in_any_contour(refs, (width - 200, height - 25))):
            count += 1
            offset = 3
        return offset if count == 1 else -1

    @staticmethod
    def _find_color_for_point(cnt_map, point_color, point):
        """Finds the color for a point from the contour map."""
        for cnt in cnt_map:
            if cnt[0] != point_color and CubeRecognition._point_in_contour(cnt[1], (int(point[0]), int(point[1]))):
                return cnt[0]
        return CubeColor.NONE
