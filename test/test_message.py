from lfgdev import Message
from lfgdev.types import MessageKind, Username


def test_encode_decode() -> None:
    message = Message(
        kind=MessageKind.HELLO,
        sent_by=Username("TestUser"),
    )
    bytes = message.encode()
    assert Message.decode(bytes) == message
