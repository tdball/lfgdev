from __future__ import annotations

import logging
import socket
import sys
from dataclasses import dataclass, field

from lfgpy._message import Message, MessageKind
from lfgpy.config import HOST
from lfgpy.types import Username

logger = logging.getLogger(__name__)


@dataclass(frozen=False, slots=True, kw_only=True)
class ClientMetadata:
    messages_sent: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class Client:
    username: Username  # TODO: This needs to be validated
    metadata: ClientMetadata = field(default_factory=ClientMetadata)

    def __post__init__(self) -> None:
        if len(self.username) > 24:
            raise ValueError("Username too long; Must be less than 24 characters")

    def connect(self) -> socket.socket:
        sock = socket.socket()
        sock.connect(HOST)
        return sock

    def send_message(self, kind: MessageKind) -> Message:
        with self.connect() as sock:
            message = Message(kind=kind, username=self.username)
            host, port = sock.getpeername()
            logger.debug(f"Request: {message}")
            sock.sendall(message.encode())
            self.metadata.messages_sent += 1
            if response := Message.from_socket(sock):
                logger.debug(f"Response from {host}:{port} - {response}")
                return response
            else:
                raise Exception(f"Empty or Invalid response from - {host}:{port}")

    def say_hello(self) -> Message:
        return self.send_message(MessageKind.HELLO)


def main() -> None:
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)
    client = Client(username=Username("HotCilantro"))
    client.send_message(MessageKind.HELLO)


if __name__ == "__main__":
    main()
