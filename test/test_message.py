from uuid import uuid4

from lfgpy.message import Message, MessageKind


def test_encode_decode() -> None:
    message = Message(
        kind=MessageKind.HELLO,
        user_id=uuid4(),
    )
    bytes = message.encode()
    assert Message.decode(bytes) == message
