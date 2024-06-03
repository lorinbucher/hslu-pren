"""Implements the web server."""
import logging
import threading

from flask import Flask


class WebServer:
    """Implements the web server used to serve the user interface."""

    def __init__(self):
        self._logger = logging.getLogger('web.server')
        self._app = Flask('PREN 3D Re-Builder', static_url_path='')
        self._thread = None

    def start(self) -> None:
        """Starts the flask webserver in a thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        """Runs the flask web server."""
        self._logger.info('Starting flask web server')
        self._add_routes()
        self._app.run(use_reloader=False)

    def _add_routes(self) -> None:
        """Add the routes that should be handled."""
        self._logger.info('Registering routes')

        @self._app.route('/test')
        def hello():
            return 'Test'
