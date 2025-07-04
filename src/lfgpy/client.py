import logging
import socket
import sys
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True, kw_only=True)
class Client:
    # Maybe combo of FriendlyName and number? Name#1234?
    # What if just string??
    user_id: UUID
    sent_messages: list[UUID] = field(default_factory=list)

    def connect(self) -> socket.socket:
        sock = socket.socket()
        sock.connect(HOST)
        return sock

    def send_message(self, kind: MessageKind) -> Message:
        with self.connect() as sock:
            message = Message(kind=kind, user_id=self.user_id)
            host, port = sock.getpeername()
            logger.debug(f"Request: {message}")
            sock.sendall(message.encode())
            self.sent_messages.append(message.identifier)
            if response := Message.from_socket(sock):
                logger.debug(f"Response from {host}:{port} - {response}")
                return response
            else:
                raise Exception(f"Empty or Invalid response from - {host}:{port}")

    def say_hello(self) -> Message:
        return self.send_message(MessageKind.HELLO)

    def login(self) -> Message:
        return self.send_message(MessageKind.CLIENT)


def main() -> None:
    client = Client(user_id=uuid4())
    client.say_hello()


if __name__ == "__main__":
    main()
