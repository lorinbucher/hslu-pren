"""Implements the UART communication protocol."""
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from serial import Serial, SerialException, SerialTimeoutException

from shared.data import AppConfiguration
from .command import Command, Message


class UartCommunicator:
    """Manages the communication with the electronics controller using the UART communication protocol."""

    def __init__(self, app_config: AppConfiguration, read_queue: queue.Queue, write_queue: queue.Queue):
        self._logger = logging.getLogger('uart.communicator')
        self._app_config = app_config
        self._read_queue = read_queue
        self._write_queue = write_queue

        self._executor = ThreadPoolExecutor(max_workers=2)
        self._halt_event = Event()

        self._ack = Event()
        self._ser_read: Serial | None = None
        self._ser_write: Serial | None = None

    def start(self) -> None:
        """Starts the UART reader and writer tasks."""
        self._logger.info('Starting UART reader and writer tasks')
        self._executor.submit(self._reader_task)
        self._executor.submit(self._writer_task)

    def halt(self) -> None:
        """Halts the UART reader and writer tasks."""
        self._logger.info('Halting UART reader and writer tasks')
        self._halt_event.set()

    def shutdown(self) -> None:
        """Shuts the executor down."""
        self._logger.info('Shutting down executor')
        self._executor.shutdown()

    def _reader_task(self) -> None:
        """Runs the UART reader task."""
        self._logger.info('UART reader task started')
        data = b''
        while not self._halt_event.is_set():
            data += self._read()
            preamble_pos = data.find(b'AAAB')
            if preamble_pos < 0:
                data = b''
                continue

            data = data[preamble_pos:]
            if len(data) >= 23:
                if self._decode(data[:23]):
                    data = data[23:]
                else:
                    data = data[4:]

        if self._ser_read is not None and self._ser_read.is_open:
            self._ser_read.close()
        self._logger.info('UART reader task stopped')

    def _writer_task(self) -> None:
        """Runs the UART writer task."""
        self._logger.info('UART writer task started')
        while not self._halt_event.is_set():
            try:
                message = self._write_queue.get(timeout=2.0)
                if not isinstance(message, Message):
                    self._logger.warning('Invalid message type: %s', type(message))
                    continue
                self._write(message)
            except queue.Empty:
                continue

        if self._ser_write is not None and self._ser_write.is_open:
            self._ser_write.close()
        self._logger.info('UART writer task stopped')

    def _read(self) -> bytes:
        """Reads data received from the UART connection."""
        try:
            if self._ser_read is None or not self._ser_read.is_open:
                self._logger.info('Opening UART read connection')
                self._ser_read = Serial(self._app_config.serial_read, self._app_config.serial_baud_rate, timeout=2.0)
            return self._ser_read.read(23)
        except (SerialException, SerialTimeoutException, ValueError) as error:
            self._logger.error('Failed to read message: %s', error)
            self._ser_read = None
            time.sleep(1)
        return bytes()

    def _write(self, command) -> None:
        """Writes the command to the UART connection."""
        message = self._encode(command)
        self._ack.clear()
        while not self._ack.is_set() and not self._halt_event.is_set():
            try:
                if self._ser_write is None or not self._ser_write.is_open:
                    self._logger.info('Opening UART write connection')
                    self._ser_write = Serial(self._app_config.serial_write, self._app_config.serial_baud_rate)

                self._logger.debug('Writing message: %s', message.hex(' '))
                self._ack.clear()
                self._ser_write.write(message)

                if self._ack.wait(timeout=2.0):
                    self._logger.debug('Received acknowledge')
                else:
                    self._logger.warning('No acknowledge received, retrying')
            except (SerialException, SerialTimeoutException, ValueError) as error:
                self._logger.error('Failed to write message: %s', error)
                self._ser_write = None
                time.sleep(1)

    def _decode(self, data: bytes) -> bool:
        """Decodes the message from the received data."""
        try:
            message_data = data[4:]
            message = Message.from_buffer_copy(message_data)
            command_type = Command(message.cmd)

            self._logger.debug('Received command: %s', command_type)
            if command_type in (Command.ACKNOWLEDGE, Command.NOT_ACKNOWLEDGE):
                self._ack.set()
            elif command_type in (Command.SEND_STATE, Command.SEND_IO_STATE, Command.EXECUTION_FINISHED):
                self._read_queue.put(message)
            else:
                self._logger.info('Unhandled command received: %s', command_type)
            return True
        except ValueError as error:
            self._logger.warning('Invalid message received: %s', error)
        return False

    @staticmethod
    def _encode(command: Message) -> bytes:
        """Encodes the command with the preamble."""
        return b'AAAB' + command
