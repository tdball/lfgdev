from lfgpy import Message
from lfgpy.types import MessageKind, Username


def test_encode_decode() -> None:
    message = Message(
        kind=MessageKind.HELLO,
        username=Username("TestUser"),
    )
    bytes = message.encode()
    assert Message.decode(bytes) == message
