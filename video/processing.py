"""Implements the video stream processing module."""
import concurrent.futures
import logging
import time
from multiprocessing import Event, Process, Queue
from typing import Any

import cv2

from shared.data import AppConfiguration, CubeConfiguration
from shared.enumerations import CubeColor
from web.api import CubeApi
from .recognition import CubeRecognition


class StreamProcessing:
    """Processes the incoming video stream."""

    def __init__(self, app_config: AppConfiguration, builder_queue: Queue):
        self._logger = logging.getLogger('video.stream_processing')
        self._app_config = app_config
        self._builder_queue = builder_queue
        self._halt = Event()
        self._recognition = Event()
        self._process: Process | None = None
        self._capture: cv2.VideoCapture | None = None
        self._cube_config = CubeConfiguration()
        self._recognition_result: dict[str, dict[str, int]] = {}

    def start(self) -> None:
        """Starts the video stream processing."""
        self._logger.info('Starting video stream processing')
        self._process = Process(target=self._run)
        self._process.start()
        self._logger.info('Video stream processing started')

    def join(self) -> None:
        """Waits for the video stream processing to complete."""
        if self._process is not None:
            self._logger.info('Waiting for video stream processing to complete')
            self._process.join()
            self._logger.info('Video stream processing completed')

    def stop(self) -> None:
        """Stops the video stream processing."""
        if self._process is not None:
            self._logger.info('Stopping video stream processing')
            self._process.close()
            self._process = None
            self._logger.info('Video stream processing stopped')

    def halt(self) -> None:
        """Sends the halt event to builder task."""
        self._logger.info('Halting video stream processing')
        self._halt.set()

    def halted(self) -> bool:
        """Returns true if the halt event is set, false if not."""
        return self._halt.is_set()

    def alive(self) -> bool:
        """Returns true if the video stream process is alive, false if not."""
        result = self._process is not None and self._process.is_alive()
        if not result:
            self._logger.warning('Video stream processing not alive')
        return result

    def start_recognition(self) -> None:
        """Starts the cube image recognition."""
        self._logger.info('Starting cube image recognition')
        self._recognition.set()
        self._cube_config.reset()
        self._recognition_result = {}

    def stop_recognition(self) -> None:
        """Stops the cube image recognition."""
        self._logger.info('Stopping cube image recognition')
        self._recognition.clear()

    def _run(self) -> None:
        """Runs the video stream process."""
        self._logger.info('Video stream process started')
        futures: list[concurrent.futures.Future] = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            while not self._halt.is_set():
                frame = self._read_frame()
                if not self._recognition.is_set():
                    continue

                if frame is not None:
                    if len(futures) <= 25:
                        future = executor.submit(CubeRecognition.process_frame, frame)
                        futures.append(future)
                    else:
                        self._logger.warning('Video stream processing overloaded, skipping frame')

                try:
                    for future in concurrent.futures.as_completed(futures, timeout=0.02):
                        self._process_result(future.result())
                        futures.remove(future)
                except concurrent.futures.TimeoutError:
                    pass

        if self._capture is not None:
            self._capture.release()
        self._logger.info('Video stream process stopped')

    def _read_frame(self) -> Any:
        """Reads the next frame of the video stream."""
        url = (f'rtsp://{self._app_config.rtsp_user}:{self._app_config.rtsp_password}'
               f'@{self._app_config.server_rtsp_address}/axis-media/media.amp'
               f'?streamprofile={self._app_config.rtsp_profile}')
        try:
            if self._capture is None or not self._capture.isOpened():
                self._logger.info('Opening video stream connection')
                self._capture = cv2.VideoCapture()
                self._capture.setExceptionMode(True)
                self._capture.open(url)

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
            cube_config = CubeConfiguration()
            cube_config.config = self._cube_config.config
            self._builder_queue.put(cube_config)
            if self._cube_config.completed():
                self._logger.info('Cube configuration completed')
                self.stop_recognition()
                cube_api = CubeApi(self._app_config)
                cube_api.post_config(cube_config)
