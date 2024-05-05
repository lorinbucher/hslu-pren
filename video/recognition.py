"""Implements the cube image recognition module."""
import logging
import multiprocessing.connection
import queue
from multiprocessing import Process, Queue

from shared.data import AppConfiguration, CubeConfiguration
from shared.enumerations import CubeColor


class CubeRecognition:
    """Performs the cube image recognition."""

    def __init__(self,
                 app_config: AppConfiguration,
                 builder_conn: multiprocessing.connection.Connection,
                 connection: multiprocessing.connection.Connection,
                 process_queue: Queue):
        self._logger = logging.getLogger('video.cube_recognition')
        self._app_config = app_config
        self._builder_conn = builder_conn
        self._connection = connection
        self._process_queue = process_queue
        self._process = Process(target=self._run)

        self._cube_config = CubeConfiguration()

    def start(self) -> None:
        """Starts the cube image recognition."""
        self._logger.info('Starting cube image recognition')
        self._cube_config.reset()
        self._process.start()
        self._logger.info('Cube image recognition started')

    def join(self) -> None:
        """Waits for the cube image recognition to complete."""
        self._logger.info('Waiting for cube image recognition to complete')
        self._process.join()
        self._logger.info('Cube image recognition completed')

    def _run(self) -> None:
        """Runs the cube image recognition process."""
        self._logger.info('Cube image recognition process started')
        counter = 0
        while not self._cube_config.completed():
            try:
                data = self._process_queue.get(block=True)
                self._logger.debug('Received data from video processing: %s', data)
                self._cube_config.set_color(counter, CubeColor.NONE)
                counter += 1
            except queue.Empty:
                self._logger.error('Video stream processing queue is empty')

        self._connection.send(True)
        self._builder_conn.send(self._cube_config)
        self._logger.info('Cube image recognition process stopped')
