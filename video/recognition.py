"""Implements the cube image recognition module."""
import logging
import multiprocessing.connection
from multiprocessing import Process, Queue

from shared.data import AppConfiguration


class CubeRecognition:
    """Performs the cube image recognition."""

    def __init__(self,
                 app_config: AppConfiguration,
                 config_conn: multiprocessing.connection.Connection,
                 connection: multiprocessing.connection.Connection,
                 process_queue: Queue):
        self._logger = logging.getLogger('video.cube_recognition')
        self._app_config = app_config
        self._config_conn = config_conn
        self._connection = connection
        self._process_queue = process_queue
        self._process = Process(target=self._run, daemon=True)

    def start(self) -> None:
        """Starts the cube image recognition."""
        self._logger.info('Starting cube image recognition')
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
        completed = False
        counter = 0
        while not completed:
            # TODO (lorin): add error handling
            data = self._process_queue.get(block=True)
            print(data)
            self._config_conn.send(data)

            counter += 1
            if counter > 10:
                completed = True
                self._connection.send(completed)

        self._logger.info('Cube image recognition process stopped')
