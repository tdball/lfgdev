from dataclasses import dataclass
from uuid import uuid4

from lfgpy.message import Message, MessageType


@dataclass(frozen=True, slots=True)
class Client:
    pass


def main() -> None:
    message = Message(identifier=uuid4(), type=MessageType.HELLO)
    data = message.to_bytes()
    message_again = Message.from_bytes(data)
    print(data, message_again)
    print("Placeholder Client")
