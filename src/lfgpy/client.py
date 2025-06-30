import logging
import socket
import sys
from dataclasses import dataclass, field
from typing import NewType

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind, get_message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

ConnectedSocket = NewType("ConnectedSocket", socket.socket)


def _default_socket() -> ConnectedSocket:
    s = socket.socket()
    s.connect(HOST)
    return ConnectedSocket(s)


@dataclass(frozen=True, slots=True)
class Client:
    _socket: ConnectedSocket = field(default_factory=_default_socket)

    def say_hello(self) -> Message | None:
        with self._socket as s:
            message = Message(kind=MessageKind.HELLO)
            s.sendall(message.encode())
            if response := get_message(self._socket):
                logger.debug(f"Response: {response}")
                return response
            return None


def main() -> None:
    client = Client()
    client.say_hello()


if __name__ == "__main__":
    main()
