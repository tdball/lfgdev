import logging
import socket
import sys
from dataclasses import dataclass, field
from typing import Self
from typing_extensions import NoReturn

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind
from lfgpy.parser import message_parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Client:
    _socket: socket.socket = field(default_factory=socket.socket)

    def __enter__(self) -> Self:
        logger.debug(f"Connecting to {HOST}")
        self._socket.connect(HOST)
        logger.debug("Connected")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        logger.debug(f"Shutting down connection to {HOST}")
        # self._socket.shutdown(socket.SHUT_WR)
        self._socket.close()
        logger.debug("Connection closed")

    def send(self, message: Message) -> Message | None:
        logger.debug(f"Sending Message: {message}")
        message.send(socket=self._socket, terminate=True)
        if response := message_parser(sock=self._socket):
            logger.debug(f"Response: {response}")
            return response
        return None


def main() -> None:
    def poll_for_input():
        match input("Press Enter to continue..."):
            case "":
                message = Message(kind=MessageKind.HELLO)
                with Client() as client:
                    if response := client.send(message):
                        if response.kind == MessageKind.MALFORMED:
                            logger.error("Malformed Message Sent")
            case _:
                logger.debug("Unsupported input")
                return

    while True:
        try:
            poll_for_input()
        except KeyboardInterrupt:
            logger.debug("Shutting Down...")
            break


if __name__ == "__main__":
    main()
