from dataclasses import dataclass
from lfgpy.model import Message, MessageType
from uuid import uuid4


@dataclass(frozen=True)
class Client:
    pass


def main() -> None:
    message = Message(identifier=uuid4(), type=MessageType.HELLO)
    data = message.to_bytes()
    message_again = Message.from_bytes(data)
    print(data, message_again)
    print("Placeholder Client")
