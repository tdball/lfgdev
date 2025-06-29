import logging
import sys
from dataclasses import dataclass
from socket import socket
from typing import Self
from uuid import uuid4

from lfgpy.config import HOST
from lfgpy.message import Message, MessageType

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Client:
    _socket = socket()

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.disconnect()

    def connect(self) -> None:
        logger.debug(f"Connecting to {HOST}")
        self._socket.connect(HOST)
        logger.debug("Connected")

    def disconnect(self) -> None:
        logger.debug(f"Shutting down connection to {HOST}")
        self._socket.close()
        logger.debug("Connection closed")

    def send_message(self, message: Message) -> None:
        logger.debug(f"Sending Message: {message}")
        self._socket.send(message.to_bytes(terminate=True))
        data = self._socket.recv(10_000)
        if response := Message.from_bytes(data):
            logger.debug(f"Response: {response}")


def main() -> None:
    with Client() as client:
        message = Message(type=MessageType.HELLO)
        client.send_message(message=message)
