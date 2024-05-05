"""Implements the video stream processing module."""
import logging
import multiprocessing.connection
import time
from multiprocessing import Process, Queue

from shared.data import AppConfiguration


class StreamProcessing:
    """Processes the incoming video stream."""

    def __init__(self,
                 app_config: AppConfiguration,
                 connection: multiprocessing.connection.Connection,
                 process_queue: Queue):
        self._logger = logging.getLogger('video.stream_processing')
        self._app_config = app_config
        self._connection = connection
        self._process_queue = process_queue
        self._process = Process(target=self._run)

    def start(self) -> None:
        """Starts the video stream processing."""
        self._logger.info('Starting video stream processing')
        self._process.start()
        self._logger.info('Video stream processing started')

    def join(self) -> None:
        """Waits for the video stream processing to complete."""
        self._logger.info('Waiting for video stream processing to complete')
        self._process.join()
        self._logger.info('Video stream processing completed')

    def _run(self) -> None:
        """Runs the video stream process."""
        self._logger.info('Video stream process started')
        completed = False
        while not completed:
            time.sleep(1)

            # TODO (lorin): add error handling
            self._process_queue.put('Test')

            if self._connection.poll():
                data = self._connection.recv()
                if isinstance(data, bool) and data:
                    completed = True

        self._logger.info('Video stream process stopped')
