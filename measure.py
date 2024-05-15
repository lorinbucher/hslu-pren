"""The 3D Re-Builder application."""
import logging
import time


class TimeMeasurement:
    """Handles the time measurement for each run."""

    def __init__(self):
        self._logger = logging.getLogger('rebuilder')
        self._start_time = 0.0
        self._stop_time = 0.0

    def reset(self) -> None:
        """Resets the time measurement."""
        self._logger.info('Resetting time measurement')
        self._start_time = 0.0
        self._stop_time = 0.0

    def start(self) -> None:
        """Starts the time measurement."""
        self._logger.info('Starting time measurement')
        self._start_time = time.perf_counter()

    def stop(self) -> None:
        """Stops the time measurement."""
        self._logger.info('Stopping time measurement')
        self._stop_time = time.perf_counter()

    def current_runtime(self) -> float:
        """Returns the current runtime."""
        return time.perf_counter() - self._start_time

    def total_runtime(self) -> float:
        """Returns the total runtime."""
        return self._stop_time - self._start_time
