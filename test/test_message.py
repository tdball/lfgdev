from lfgpy.message import Message, MessageType


def test_conversion() -> None:
    pre = Message(type=MessageType.HELLO)
    raw = pre.to_bytes()
    post = Message.from_bytes(raw)
    assert pre == post
