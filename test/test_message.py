from lfgpy.message import Message, MessageKind


def test_conversion() -> None:
    message = Message(kind=MessageKind.HELLO)
    as_bytes = message.encode()
    assert message == Message.decode(as_bytes)
