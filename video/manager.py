"""Implements the image recognition manager."""
import logging
import multiprocessing.connection
import queue
from multiprocessing import Pipe, Queue

from shared.data import AppConfiguration
from video.processing import StreamProcessing
from video.recognition import CubeRecognition


class RecognitionManager:
    """Manages the stream processing and image recognition tasks."""

    def __init__(self, app_config: AppConfiguration, builder_conn: multiprocessing.connection.Connection):
        self._logger = logging.getLogger('video.manager')
        self._conn_recv, self._conn_send = Pipe(duplex=False)
        self._process_queue: Queue = Queue(maxsize=1000)
        self._stream_processing = StreamProcessing(app_config, self._conn_recv, self._process_queue)
        self._cube_recognition = CubeRecognition(app_config, builder_conn, self._conn_send, self._process_queue)

    def start(self) -> None:
        """Starts the video stream processing and cube image recognition tasks."""
        self._logger.info('Starting tasks')
        self._stream_processing.start()
        self._cube_recognition.start()
        self._logger.info('Tasks started')

    def join(self) -> None:
        """Waits for the video stream processing and cube image recognition tasks to complete."""
        self._logger.info('Waiting for tasks to complete')
        self._stream_processing.join()
        self._cube_recognition.join()
        self._logger.info('Tasks completed')

    def clear_queue(self) -> None:
        """Clears the processing queue."""
        self._logger.info('Clearing processing queue')
        try:
            while not self._process_queue.empty():
                self._process_queue.get(block=False)
        except queue.Empty:
            self._logger.error('Video processing queue is empty')

        self._logger.info('Processing queue cleared')
