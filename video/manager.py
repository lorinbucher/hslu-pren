"""Implements the image recognition manager."""
import logging
from multiprocessing import Event, Queue

from shared.data import AppConfiguration
from video.processing import StreamProcessing
from video.recognition import CubeRecognition


class RecognitionManager:
    """Manages the stream processing and image recognition tasks."""

    def __init__(self, app_config: AppConfiguration, builder_queue: Queue):
        self._logger = logging.getLogger('video.manager')
        self._halt_processing = Event()
        self._halt_recognition = Event()
        self._process_queue: Queue = Queue(maxsize=25)
        self._stream_processing = StreamProcessing(app_config, self._halt_processing, self._process_queue)
        self._cube_recognition = CubeRecognition(app_config, self._halt_recognition, builder_queue, self._process_queue)

    def start(self, processing: bool = True, recognition: bool = True) -> None:
        """Starts the video stream processing and/or cube image recognition tasks."""
        if processing:
            self._halt_processing.clear()
            self._stream_processing.start()
        if recognition:
            self._halt_recognition.clear()
            self._cube_recognition.start()

    def join(self, processing: bool = True, recognition: bool = True) -> None:
        """Waits for the video stream processing and/or cube image recognition tasks to complete."""
        if processing:
            self._stream_processing.join()
        if recognition:
            self._cube_recognition.join()

    def stop(self, processing: bool = True, recognition: bool = True) -> None:
        """Stops the video stream processing and/or cube image recognition tasks."""
        if processing:
            self._stream_processing.stop()
        if recognition:
            self._cube_recognition.stop()

    def halt(self, processing: bool = True, recognition: bool = True) -> None:
        """Sends the halt event to the stream processing and/or cube image recognition tasks."""
        if processing:
            self._halt_processing.set()
        if recognition:
            self._halt_recognition.set()

    def alive(self, processing: bool = True, recognition: bool = True) -> bool:
        """Checks if the stream processing and/or cube image recognition tasks are alive."""
        if processing and recognition:
            return self._stream_processing.alive() and self._cube_recognition.alive()
        elif processing:
            return self._stream_processing.alive()
        elif recognition:
            return self._cube_recognition.alive()
        return False
