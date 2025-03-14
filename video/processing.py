"""Implements the video stream processing module."""
import concurrent.futures
import logging
import queue
import time
from threading import Event, Thread
from typing import Any

import cv2

from shared.data import AppConfiguration, CubeConfiguration
from shared.enumerations import CubeColor
from .recognition import CubeRecognition


class StreamProcessing:
    """Processes the incoming video stream."""

    def __init__(self, app_config: AppConfiguration, builder_queue: queue.Queue):
        self._logger = logging.getLogger('video.stream_processing')
        self._app_config = app_config
        self._builder_queue = builder_queue
        self._halt_event = Event()
        self._recognition = Event()
        self._thread: Thread | None = None
        self._capture: cv2.VideoCapture | None = None
        self._cube_config = CubeConfiguration()
        self._recognition_result: dict[str, dict[str, int]] = {}

    def start(self) -> None:
        """Starts the video stream processing."""
        self._logger.info('Starting video stream processing')
        self._halt_event.clear()
        self._thread = Thread(target=self._run)
        self._thread.start()
        self._logger.info('Video stream processing started')

    def stop(self) -> None:
        """Stops the video stream processing."""
        if self._thread is not None:
            self._logger.info('Stopping video stream processing')
            self._thread.join()
            self._thread = None
            self._logger.info('Video stream processing stopped')

    def halt(self) -> None:
        """Sends the halt event to builder task."""
        self._logger.info('Halting video stream processing')
        self._halt_event.set()

    def start_recognition(self) -> None:
        """Starts the cube image recognition."""
        self._logger.info('Starting cube image recognition')
        self._recognition.set()

    def stop_recognition(self) -> None:
        """Stops the cube image recognition."""
        self._logger.info('Stopping cube image recognition')
        self._recognition.clear()

    def _run(self) -> None:
        """Runs the video stream process."""
        self._logger.info('Video stream process started')
        futures: list[concurrent.futures.Future] = []
        frame_queue: queue.Queue = queue.Queue(maxsize=250)
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            while not self._halt_event.is_set():
                frame = self._read_frame()
                try:
                    if frame is not None:
                        if frame_queue.full():
                            frame_queue.get_nowait()
                        frame_queue.put(frame)

                        if not self._recognition.is_set():
                            self._cube_config.reset()
                            self._recognition_result = {}
                        else:
                            while not frame_queue.empty() and len(futures) <= 50:
                                future = executor.submit(CubeRecognition.process_frame, frame_queue.get_nowait())
                                futures.append(future)

                        for future in concurrent.futures.as_completed(futures, timeout=0.02):
                            self._process_result(future.result())
                            futures.remove(future)
                except (concurrent.futures.TimeoutError, queue.Empty, queue.Full):
                    pass

        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._logger.info('Video stream process stopped')

    def _read_frame(self) -> Any:
        """Reads the next frame of the video stream."""
        url = (f'rtsp://{self._app_config.rtsp_user}:{self._app_config.rtsp_password}'
               f'@{self._app_config.rtsp_address}/axis-media/media.amp'
               f'?streamprofile={self._app_config.rtsp_profile}')
        try:
            if self._capture is None or not self._capture.isOpened():
                self._logger.info('Opening video stream connection')
                self._capture = cv2.VideoCapture()
                self._capture.setExceptionMode(True)
                self._capture.open(url, apiPreference=cv2.CAP_FFMPEG, params=[
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, 2000
                ])

            if self._capture.grab():
                res, frame = self._capture.retrieve()
                return CubeRecognition.crop_frame(frame) if res else self._capture.release()
        except cv2.error as error:
            self._logger.error('Failed to read frame: %s', error)
            self._capture = None
            time.sleep(0.25)
        return None

    def _process_result(self, config: list[CubeColor]) -> None:
        """Processes the result of the cube image recognition."""
        changed = False
        for pos, color in enumerate(config, start=1):
            colors_at_pos = self._recognition_result.get(str(pos), {})
            color_set = self._cube_config.get_color(pos) != CubeColor.UNKNOWN
            count = colors_at_pos.get(color, 0) + 1
            if not color_set and color != CubeColor.UNKNOWN and count >= self._app_config.app_confidence:
                self._cube_config.set_color(color, pos)
                changed = True

            colors_at_pos[color] = count
            self._recognition_result[str(pos)] = colors_at_pos

        if changed:
            self._logger.info('Cube configuration changed: %s', self._cube_config.to_dict())
            self._builder_queue.put(self._cube_config)
            if self._cube_config.completed():
                self._logger.info('Cube configuration completed')
