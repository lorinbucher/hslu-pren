"""Implements the video stream processing module."""
import logging
import queue
import time
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event

from shared.data import AppConfiguration


class StreamProcessing:
    """Processes the incoming video stream."""

    def __init__(self, app_config: AppConfiguration, terminate: Event, process_queue: Queue):
        self._logger = logging.getLogger('video.stream_processing')
        self._app_config = app_config
        self._terminate = terminate
        self._process_queue = process_queue
        self._process: Process | None = None

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

    def _run(self) -> None:
        """Runs the video stream process."""
        self._logger.info('Video stream process started')
        while not self._terminate.is_set():
            time.sleep(0.5)

            try:
                self._process_queue.put('Test', block=False)
            except queue.Full:
                self._logger.warning('Video stream processing queue is full')

        self._logger.info('Video stream process stopped')
