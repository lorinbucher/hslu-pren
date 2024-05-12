"""Implements the image recognition manager."""
import logging
from multiprocessing import Event, Queue, SimpleQueue

from shared.data import AppConfiguration
from video.processing import StreamProcessing
from video.recognition import CubeRecognition


class RecognitionManager:
    """Manages the stream processing and image recognition tasks."""

    def __init__(self, app_config: AppConfiguration, builder_queue: SimpleQueue):
        self._logger = logging.getLogger('video.manager')
        self._terminate = Event()
        self._process_queue: Queue = Queue(maxsize=1000)
        self._stream_processing = StreamProcessing(app_config, self._terminate, self._process_queue)
        self._cube_recognition = CubeRecognition(app_config, self._terminate, builder_queue, self._process_queue)

    def start(self) -> None:
        """Starts the video stream processing and cube image recognition tasks."""
        self._logger.info('Starting tasks')
        self._terminate.clear()
        self._stream_processing.start()
        self._cube_recognition.start()
        self._logger.info('Tasks started')

    def join(self) -> None:
        """Waits for the video stream processing and cube image recognition tasks to complete."""
        self._logger.info('Waiting for tasks to complete')
        self._stream_processing.join()
        self._cube_recognition.join()
        self._logger.info('Tasks completed')

    def stop(self) -> None:
        """Stops the video stream processing and cube image recognition tasks."""
        self._logger.info('Stopping tasks')
        self._stream_processing.stop()
        self._cube_recognition.stop()
        self._logger.info('Tasks stopped')

    def terminate_signal(self) -> None:
        """Sends the terminate event to the stream processing and cube image recognition tasks."""
        self._terminate.set()
