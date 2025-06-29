from lfgpy.message import Message, MessageKind


def test_conversion() -> None:
    pre = Message(kind=MessageKind.HELLO)
    raw = bytes(pre)
    post = Message.from_bytes(raw)
    assert pre == post
