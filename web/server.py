"""Implements the web server."""
import logging
import queue
import threading
from typing import Any

from flask import Flask, jsonify, request

from shared.config import read_config_file, write_config_file
from shared.enumerations import Action


class WebServer:
    """Implements the web server used to serve the user interface."""

    def __init__(self, web_queue: queue.Queue):
        self._logger = logging.getLogger('web.server')
        self._web_queue = web_queue
        self._app = Flask('PREN 3D Re-Builder', static_url_path='')
        self._thread: threading.Thread | None = None

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

        @self._app.route('/action', methods=['POST'])
        def _action():
            data = request.get_json()
            self._logger.info('Received action request: %s', data)
            try:
                action = Action(data.get('action', ''))
                self._web_queue.put(action)
            except (KeyError, ValueError) as error:
                self._logger.warning('Invalid action data: %s', error)
                return 'Invalid action', 400
            return 'OK', 200

        @self._app.route('/settings', methods=['GET', 'POST'])
        def _settings():
            if request.method == 'GET':
                settings = read_config_file().get('app', {})
                self._logger.info('Current settings: %s', settings)
                return jsonify(settings), 200

            if request.method == 'POST':
                data = request.get_json()
                self._logger.info('Received settings request: %s', data)
                if not self._validate_settings(data):
                    self._logger.warning('Invalid settings data')
                    return 'Invalid data', 400

                config = read_config_file()
                config['app'] = data
                write_config_file(config)
                return 'OK', 200

        @self._app.route('/status', methods=['GET'])
        def _status():
            return jsonify({}), 200

    @staticmethod
    def _validate_settings(data: dict[str, Any]) -> bool:
        """Validates the settings data."""
        if len(data.keys()) != 5:
            return False
        for key, value in data.items():
            if key in ('confidence', 'recognition_timeout'):
                if not isinstance(value, int) or value <= 0:
                    return False
            elif key in ('efficiency_mode', 'fast_mode', 'incremental_build'):
                if not isinstance(value, bool):
                    return False
            else:
                return False
        return True
