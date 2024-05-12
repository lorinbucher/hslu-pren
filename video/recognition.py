"""Implements the cube image recognition module."""
import logging
import queue
from multiprocessing import Process, Queue, SimpleQueue
from multiprocessing.synchronize import Event

from shared.data import AppConfiguration, CubeConfiguration
from shared.enumerations import CubeColor


class CubeRecognition:
    """Performs the cube image recognition."""

    def __init__(self, app_config: AppConfiguration, terminate: Event,
                 builder_queue: SimpleQueue, process_queue: Queue):
        self._logger = logging.getLogger('video.cube_recognition')
        self._app_config = app_config
        self._terminate = terminate
        self._builder_queue = builder_queue
        self._process_queue = process_queue

        self._process: Process | None = None
        self._cube_config = CubeConfiguration()

    def start(self) -> None:
        """Starts the cube image recognition."""
        self._logger.info('Starting cube image recognition')
        self._cube_config.reset()
        self._process = Process(target=self._run)
        self._process.start()
        self._logger.info('Cube image recognition started')

    def join(self) -> None:
        """Waits for the cube image recognition to complete."""
        if self._process is not None:
            self._logger.info('Waiting for cube image recognition to complete')
            self._process.join()
            self._logger.info('Cube image recognition completed')

    def stop(self) -> None:
        """Stops the cube image recognition."""
        if self._process is not None:
            self._logger.info('Stopping cube image recognition')
            self._process.close()
            self._process = None
            self._logger.info('Cube image recognition stopped')

    def _run(self) -> None:
        """Runs the cube image recognition process."""
        self._logger.info('Cube image recognition process started')
        counter = 0
        while not self._terminate.is_set() or self._cube_config.completed():
            try:
                data = self._process_queue.get(block=True)
                self._logger.debug('Received data from video processing: %s', data)
                self._cube_config.set_color(counter, CubeColor.NONE)
                counter += 1
            except queue.Empty:
                self._logger.error('Video stream processing queue is empty')

        self._builder_queue.put(self._cube_config)
        self._logger.info('Cube image recognition process stopped')
