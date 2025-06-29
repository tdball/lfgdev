import logging
import sys
from dataclasses import dataclass
from socket import socket
from typing import Self

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Client:
    _socket = socket()

    def __enter__(self) -> Self:
        logger.debug(f"Connecting to {HOST}")
        self._socket.connect(HOST)
        logger.debug("Connected")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        logger.debug(f"Shutting down connection to {HOST}")
        self._socket.close()
        logger.debug("Connection closed")

    def send_message(self, message: Message) -> None:
        logger.debug(f"Sending Message: {message}")
        message.send(socket=self._socket, terminate=True)
        # FIXME: This doesn't clear after the first recv, empty the socket... buffer?
        data = self._socket.recv(28)
        if response := Message.from_bytes(data):
            logger.debug(f"Response: {response}")


def main() -> None:
    with Client() as client:
        while True:
            match input("Continue?: ").lower():
                case "y":
                    message = Message(kind=MessageKind.HELLO)
                    client.send_message(message=message)
                case _:
                    break
