import logging
import socket
import sys
from dataclasses import dataclass, field

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind, get_message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Client:
    _socket: socket.socket = field(default_factory=socket.socket)

    def say_hello(self) -> Message | None:
        self._socket.connect(HOST)
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
